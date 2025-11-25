from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator

from agents import RunConfig, Runner
from agents.model_settings import ModelSettings
from chatkit.agents import stream_agent_response
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.types import Attachment, ThreadMetadata, ThreadStreamEvent, UserMessageItem
from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import Response, StreamingResponse
from openai.types.responses import EasyInputMessageParam, ResponseInputContentParam, ResponseInputTextParam
from starlette.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware

from .car_agent import CarAgentContext, car_sales_agent, inventory_state
from .car_inventory import CarInventoryStore
from .memory_store import MemoryStore
from .thread_item_converter import CarScoutThreadItemConverter
from .title_agent import title_agent


def _inventory_context_block(
    thread_id: str, inventory: CarInventoryStore
) -> EasyInputMessageParam:
    summary = inventory.build_context_block(thread_id)
    return EasyInputMessageParam(
        type="message",
        role="user",
        content=[ResponseInputTextParam(type="input_text", text=summary)],
    )


class CarScoutServer(ChatKitServer[dict[str, Any]]):
    def __init__(self, inventory: CarInventoryStore) -> None:
        store = MemoryStore()
        super().__init__(store)
        self.store = store
        self.inventory = inventory
        self.agent = car_sales_agent
        self.title_agent = title_agent
        self.thread_item_converter = CarScoutThreadItemConverter()

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

        inventory_item = _inventory_context_block(thread.id, self.inventory)
        agent_input = [inventory_item] + (await self.thread_item_converter.to_agent_input(items))

        agent_context = CarAgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
            inventory=self.inventory,
        )
        result = Runner.run_streamed(
            self.agent,
            agent_input,
            context=agent_context,
            run_config=RunConfig(model_settings=ModelSettings(temperature=0.35)),
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
        raise RuntimeError("File attachments are not supported in this demo.")


def get_server() -> CarScoutServer:
    return car_scout_server


def _thread_id_or_default(thread_id: str | None) -> str | None:
    return thread_id or None


car_scout_server = CarScoutServer(inventory=inventory_state)

app = FastAPI(title="ChatKit Car Scout API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/autos/chatkit")
async def chatkit_endpoint(
    request: Request, server: CarScoutServer = Depends(get_server)
) -> Response:
    payload = await request.body()
    result = await server.process(payload, {"request": request})
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)


@app.get("/autos/cars")
async def inventory_snapshot(
    thread_id: str | None = Query(None, description="ChatKit thread identifier"),
) -> dict[str, Any]:
    data = inventory_state.snapshot(_thread_id_or_default(thread_id))
    return {"inventory": data}


@app.get("/autos/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
