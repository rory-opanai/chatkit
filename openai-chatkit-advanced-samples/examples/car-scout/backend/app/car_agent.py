from __future__ import annotations

from typing import Annotated, Any

from agents import Agent, RunContextWrapper, function_tool
from chatkit.agents import AgentContext
from pydantic import BaseModel, ConfigDict, Field

from .car_inventory import CarInventoryStore, CarRecord, load_inventory

CAR_AGENT_INSTRUCTIONS = """
You are Scout, a personable dealership guide who helps shoppers narrow inventory.
Keep the tone casual, skip sales cliches, and keep answers to 2 short paragraphs max.

Workflow expectations:
- Always call `search_inventory` before giving recommendations so you respond with
  the actual cars available.
- Ask quick clarifying questions when key info is missing (budget, seats, powertrain).
- Summaries should highlight 2-3 standout matches and why they fit.
- Mention the next filter to confirm so the shopper feels guided.
- If no cars match, call out what's missing and suggest relaxing one constraint.
- Use `reset_inventory_filters` when the shopper wants to start from scratch.
- When the shopper is satisfied, point them to the "More information" buttons in the
  results panel to view the listing.
""".strip()

MODEL = "gpt-4.1-mini"


class CarAgentContext(AgentContext):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    inventory: Annotated[CarInventoryStore, Field(exclude=True)]


class CarSummary(BaseModel):
    id: str
    name: str
    price: int
    mileage: int
    body_style: str
    drivetrain: str
    fuel_type: str
    location: str
    listing_url: str

    @classmethod
    def from_record(cls, car: CarRecord) -> "CarSummary":
        return cls(
            id=car.id,
            name=car.display_name(),
            price=car.price,
            mileage=car.mileage,
            body_style=car.body_style,
            drivetrain=car.drivetrain,
            fuel_type=car.fuel_type,
            location=car.location,
            listing_url=car.listing_url,
        )


class CarSearchResult(BaseModel):
    total: int
    filters: dict[str, Any]
    cars: list[CarSummary]


class CarFilterCriteria(BaseModel):
    price_min: int | None = Field(None, description="Minimum budget in USD")
    price_max: int | None = Field(None, description="Maximum budget in USD")
    seats_min: int | None = Field(None, description="Minimum seats needed")
    max_mileage: int | None = Field(None, description="Upper bound for odometer")
    min_year: int | None = Field(None, description="Earliest acceptable model year")
    makes: list[str] | None = None
    body_styles: list[str] | None = None
    drivetrains: list[str] | None = None
    fuel_types: list[str] | None = None
    must_have_features: list[str] | None = None
    locations: list[str] | None = None

    def to_update(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)


inventory_state = load_inventory()


def _thread_id(ctx: RunContextWrapper[CarAgentContext]) -> str:
    return ctx.context.thread.id


@function_tool(description_override="Show available inventory without narrowing filters.")
async def list_inventory(
    ctx: RunContextWrapper[CarAgentContext],
    limit: int = 6,
) -> CarSearchResult:
    inventory = ctx.context.inventory
    cars = inventory.initial_matches()[: max(1, limit)]
    profile = inventory.get_profile(_thread_id(ctx))
    return CarSearchResult(
        total=len(inventory.initial_matches()),
        filters=profile.filters.to_payload(),
        cars=[CarSummary.from_record(car) for car in cars],
    )


@function_tool(description_override="Filter inventory using the shopper's criteria.")
async def search_inventory(
    ctx: RunContextWrapper[CarAgentContext],
    criteria: CarFilterCriteria,
) -> CarSearchResult:
    inventory = ctx.context.inventory
    matches = inventory.update_filters(_thread_id(ctx), criteria.to_update())
    profile = inventory.get_profile(_thread_id(ctx))
    return CarSearchResult(
        total=len(matches),
        filters=profile.filters.to_payload(),
        cars=[CarSummary.from_record(car) for car in matches[:8]],
    )


@function_tool(description_override="Clear all filters and restart from the full inventory.")
async def reset_inventory_filters(
    ctx: RunContextWrapper[CarAgentContext],
) -> CarSearchResult:
    inventory = ctx.context.inventory
    profile = inventory.reset_profile(_thread_id(ctx))
    matches = inventory.initial_matches()
    return CarSearchResult(
        total=len(matches),
        filters=profile.filters.to_payload(),
        cars=[CarSummary.from_record(car) for car in matches[:8]],
    )


@function_tool(description_override="Recap the shopper's saved preferences.")
async def get_current_preferences(
    ctx: RunContextWrapper[CarAgentContext],
) -> dict[str, Any]:
    inventory = ctx.context.inventory
    summary = inventory.build_context_block(_thread_id(ctx))
    return {"profile": summary}


def build_car_agent() -> Agent[CarAgentContext]:
    tools = [list_inventory, search_inventory, reset_inventory_filters, get_current_preferences]
    return Agent[CarAgentContext](
        model=MODEL,
        name="Scout",
        instructions=CAR_AGENT_INSTRUCTIONS,
        tools=tools,  # type: ignore[arg-type]
    )


def create_agent() -> Agent[CarAgentContext]:
    return build_car_agent()


car_sales_agent = build_car_agent()
