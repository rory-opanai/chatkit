from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator

from agents import RunConfig, Runner
from agents.model_settings import ModelSettings
from chatkit.agents import stream_agent_response
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.types import Attachment, ThreadMetadata, ThreadStreamEvent, UserMessageItem
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from openai.types.responses import EasyInputMessageParam, ResponseInputContentParam, ResponseInputTextParam
from starlette.responses import JSONResponse

from .listing_agent import ListingAgentContext, listing_agent, listing_store
from .listing_store import ListingStore
from .memory_store import MemoryStore
from .thread_item_converter import ListingThreadItemConverter
from .title_agent import title_agent


def _listing_block(thread_id: str, store: ListingStore) -> EasyInputMessageParam:
    summary = store.build_context_block(thread_id)
    return EasyInputMessageParam(
        type="message",
        role="user",
        content=[ResponseInputTextParam(type="input_text", text=summary)],
    )


class ListingServer(ChatKitServer[dict[str, Any]]):
    def __init__(self, listing_store: ListingStore) -> None:
        store = MemoryStore()
        super().__init__(store)
        self.store = store
        self.listing_store = listing_store
        self.agent = listing_agent
        self.title_agent = title_agent
        self.thread_item_converter = ListingThreadItemConverter()

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        items_page = await self.store.load_thread_items(thread.id, None, 20, "desc", context)
        updating_thread_title = asyncio.create_task(
            self.maybe_update_thread_title(thread, input_user_message)
        )
        items = list(reversed(items_page.data))

        listing_item = _listing_block(thread.id, self.listing_store)
        agent_input = [listing_item] + (await self.thread_item_converter.to_agent_input(items))

        agent_context = ListingAgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )
        result = Runner.run_streamed(
            self.agent,
            agent_input,
            context=agent_context,
            run_config=RunConfig(model_settings=ModelSettings(temperature=0.3)),
        )

        async for event in stream_agent_response(agent_context, result):
            yield event

        await updating_thread_title

    async def maybe_update_thread_title(
        self, thread: ThreadMetadata, user_message: UserMessageItem | None
    ) -> None:
        if user_message is None or thread.title is not None:
            return

        run = await Runner.run(
            title_agent,
            input=await self.thread_item_converter.to_agent_input(user_message),
        )
        model_result: str = run.final_output
        if not model_result:
            return
        model_result = model_result[:1].upper() + model_result[1:]
        thread.title = model_result.strip(".")

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise HTTPException(status_code=400, detail="File attachments are not supported.")


listing_server = ListingServer(listing_store)

app = FastAPI(title="ChatKit Car Listing Builder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_server() -> ListingServer:
    return listing_server


@app.post("/listing/chatkit")
async def chatkit_endpoint(
    request: Request, server: ListingServer = Depends(get_server)
) -> Response:
    payload = await request.body()
    result = await server.process(payload, {"request": request})
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)


@app.get("/listing/draft")
async def read_listing(
    thread_id: str | None = Query(None, description="ChatKit thread identifier"),
    server: ListingServer = Depends(get_server),
) -> dict[str, Any]:
    snapshot = listing_store.snapshot(thread_id)
    return {"listing": snapshot}


@app.post("/listing/draft/submit")
async def submit_listing(
    thread_id: str = Query(..., description="ChatKit thread identifier"),
) -> dict[str, Any]:
    try:
        record = listing_store.submit(thread_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "status": record.status,
        "submitted_at": record.submitted_at.isoformat() if record.submitted_at else None,
    }


@app.post("/listing/draft/reset")
async def reset_listing(
    thread_id: str = Query(..., description="ChatKit thread identifier"),
) -> dict[str, Any]:
    record = listing_store.reset(thread_id)
    return {"listing": record.to_payload()}


@app.get("/listing/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
