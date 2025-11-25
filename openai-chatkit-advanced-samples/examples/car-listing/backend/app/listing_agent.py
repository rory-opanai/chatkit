from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from agents import Agent, RunContextWrapper, StopAtTools, function_tool
from chatkit.agents import AgentContext
from pydantic import BaseModel, ConfigDict, Field

from .listing_store import LIST_FIELDS, ListingStore, REQUIRED_FIELDS
from .memory_store import MemoryStore

MODEL = "gpt-4.1-mini"

INSTRUCTIONS = """
You are a helpful listing coordinator. Collect every field needed for a complete car listing
and keep the tone clean and direct.

Workflow:
- Start by calling `get_listing_status` to see what fields are still missing.
- In your first response, list all required fields (seller name, email, phone, make, model, year,
  trim, body style, fuel type, transmission, drivetrain, colour, mileage, asking price, location,
  MOT expiry, service history, key features list, photo URLs) with a short description or examples.
- Ask for only one or two pieces of info per turn so it feels like a short checklist.
- Whenever the user supplies new info, call `update_listing_details` immediately with the structured data.
- Confirm back what you captured in natural language (“Got it: 2019 Aurora Sprint in midnight blue.”).
- You must draft the listing description yourself once enough details exist—do not ask the user to write it.
- The listing title should be composed automatically from year, make, and model.
- Use metric-friendly numbers (mileage in miles, price in GBP with £).
- When all required fields are filled and the user is happy, call `submit_listing`.
- If the user wants to start over, tell them to press the "Submit Another" button.

Required fields: seller name, email, phone, make, model, year, trim, body style, fuel type,
transmission, drivetrain, color, mileage, asking price, location, MOT expiry, service history,
description, key features (list), photo URLs (list). Keep prompting until every field is filled.
""".strip()


class ListingAgentContext(AgentContext):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    store: Annotated[MemoryStore, Field(exclude=True)]


class ListingDetailsInput(BaseModel):
    seller_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    make: str | None = None
    model: str | None = None
    year: int | None = None
    trim: str | None = None
    body_style: str | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    drivetrain: str | None = None
    color: str | None = None
    mileage: int | None = None
    asking_price: int | None = None
    location: str | None = None
    mot_expiry: str | None = None
    service_history: str | None = None
    description: str | None = None
    key_features: list[str] | None = None
    photo_urls: list[str] | None = None

    def to_update(self) -> dict[str, Any]:
        payload = self.model_dump(exclude_none=True)
        for field in LIST_FIELDS:
            if field in payload and isinstance(payload[field], list):
                payload[field] = [item.strip() for item in payload[field] if item and item.strip()]
        return payload


listing_store = ListingStore()


def _thread_id(ctx: RunContextWrapper[ListingAgentContext]) -> str:
    return ctx.context.thread.id


@function_tool(description_override="Review the current listing progress and missing fields.")
async def get_listing_status(
    ctx: RunContextWrapper[ListingAgentContext],
) -> dict[str, Any]:
    data = listing_store.snapshot(_thread_id(ctx))
    data["required_fields"] = REQUIRED_FIELDS
    return data


@function_tool(description_override="Update the structured listing details gathered from the user.")
async def update_listing_details(
    ctx: RunContextWrapper[ListingAgentContext],
    details: ListingDetailsInput,
) -> dict[str, Any]:
    listing_store.update(_thread_id(ctx), details.to_update())
    data = listing_store.snapshot(_thread_id(ctx))
    return {"missing_fields": data["missing_fields"], "completed": data["completed"]}


@function_tool(description_override="Submit the listing once every required field has been captured.")
async def submit_listing(
    ctx: RunContextWrapper[ListingAgentContext],
) -> dict[str, Any]:
    record = listing_store.submit(_thread_id(ctx))
    return {
        "submitted_at": record.submitted_at.isoformat() if record.submitted_at else datetime.utcnow().isoformat(),
        "status": record.status,
    }


def build_listing_agent() -> Agent[ListingAgentContext]:
    tools = [get_listing_status, update_listing_details, submit_listing]
    return Agent[ListingAgentContext](
        model=MODEL,
        name="Listing Coordinator",
        instructions=INSTRUCTIONS,
        tools=tools,  # type: ignore[arg-type]
        tool_use_behavior=StopAtTools(stop_at_tool_names=[submit_listing.name]),
    )


listing_agent = build_listing_agent()
