from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence


@dataclass
class CarRecord:
    id: str
    make: str
    model: str
    trim: str
    year: int
    price: int
    mileage: int
    body_style: str
    drivetrain: str
    fuel_type: str
    seats: int
    range_miles: int | None
    color: str
    location: str
    description: str
    features: list[str]
    listing_url: str
    image_url: str

    def display_name(self) -> str:
        trim = f" {self.trim}" if self.trim else ""
        return f"{self.year} {self.make} {self.model}{trim}".strip()

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.display_name(),
            "make": self.make,
            "model": self.model,
            "trim": self.trim,
            "year": self.year,
            "price": self.price,
            "mileage": self.mileage,
            "body_style": self.body_style,
            "drivetrain": self.drivetrain,
            "fuel_type": self.fuel_type,
            "seats": self.seats,
            "range_miles": self.range_miles,
            "color": self.color,
            "location": self.location,
            "description": self.description,
            "features": self.features,
            "listing_url": self.listing_url,
            "image_url": self.image_url,
        }


@dataclass
class CarFilters:
    price_min: int | None = None
    price_max: int | None = None
    makes: list[str] = field(default_factory=list)
    body_styles: list[str] = field(default_factory=list)
    drivetrains: list[str] = field(default_factory=list)
    fuel_types: list[str] = field(default_factory=list)
    seats_min: int | None = None
    max_mileage: int | None = None
    min_year: int | None = None
    must_have_features: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        values: Sequence[Any] = (
            self.price_min,
            self.price_max,
            self.seats_min,
            self.max_mileage,
            self.min_year,
            self.makes,
            self.body_styles,
            self.drivetrains,
            self.fuel_types,
            self.must_have_features,
            self.locations,
        )
        return all(value in (None, [], "") for value in values)

    def to_payload(self) -> dict[str, Any]:
        return {
            "price_min": self.price_min,
            "price_max": self.price_max,
            "makes": self.makes,
            "body_styles": self.body_styles,
            "drivetrains": self.drivetrains,
            "fuel_types": self.fuel_types,
            "seats_min": self.seats_min,
            "max_mileage": self.max_mileage,
            "min_year": self.min_year,
            "must_have_features": self.must_have_features,
            "locations": self.locations,
        }


@dataclass
class CarSearchProfile:
    filters: CarFilters = field(default_factory=CarFilters)
    match_ids: list[str] = field(default_factory=list)

    def update_matches(self, matches: Iterable[CarRecord]) -> None:
        self.match_ids = [car.id for car in matches]


class CarInventoryStore:
    def __init__(self, data_path: Path) -> None:
        raw = json.loads(data_path.read_text())
        self._inventory = [CarRecord(**entry) for entry in raw]
        self._inventory_by_id = {car.id: car for car in self._inventory}
        self._profiles: dict[str, CarSearchProfile] = {}

    def initial_matches(self) -> list[CarRecord]:
        return list(self._inventory)

    def get_profile(self, thread_id: str | None) -> CarSearchProfile:
        if not thread_id:
            profile = CarSearchProfile()
            profile.update_matches(self.initial_matches())
            return profile
        if thread_id not in self._profiles:
            profile = CarSearchProfile()
            profile.update_matches(self.initial_matches())
            self._profiles[thread_id] = profile
        return self._profiles[thread_id]

    def reset_profile(self, thread_id: str) -> CarSearchProfile:
        profile = CarSearchProfile()
        profile.update_matches(self.initial_matches())
        self._profiles[thread_id] = profile
        return profile

    def update_filters(self, thread_id: str, update: dict[str, Any]) -> list[CarRecord]:
        profile = self.get_profile(thread_id)
        filters = profile.filters
        self._apply_update(filters, update)
        matches = self._apply_filters(filters)
        if matches:
            profile.update_matches(matches)
            return matches

        if update:
            fresh = CarFilters()
            self._apply_update(fresh, update)
            fallback_matches = self._apply_filters(fresh)
            if fallback_matches:
                profile.filters = fresh
                profile.update_matches(fallback_matches)
                return fallback_matches

        profile.update_matches(matches)
        return matches

    def _apply_update(self, filters: CarFilters, update: dict[str, Any]) -> None:
        if "price_min" in update:
            filters.price_min = update.get("price_min")
        if "price_max" in update:
            filters.price_max = update.get("price_max")
        if "seats_min" in update:
            filters.seats_min = update.get("seats_min")
        if "max_mileage" in update:
            filters.max_mileage = update.get("max_mileage")
        if "min_year" in update:
            filters.min_year = update.get("min_year")
        for key in ("makes", "body_styles", "drivetrains", "fuel_types", "must_have_features", "locations"):
            if key in update and update[key] is not None:
                value = update[key]
                if isinstance(value, str):
                    setattr(filters, key, [value])
                else:
                    setattr(filters, key, [str(item) for item in value if item])

    def snapshot(self, thread_id: str | None) -> dict[str, Any]:
        profile = self.get_profile(thread_id)
        cars = self._resolve_matches(profile)
        return {
            "filters": profile.filters.to_payload(),
            "cars": [car.to_payload() for car in cars],
            "total": len(cars),
        }

    def build_context_block(self, thread_id: str) -> str:
        profile = self.get_profile(thread_id)
        filters = profile.filters
        cars = self._resolve_matches(profile)
        summary_lines = ["<CAR_SEARCH_PROFILE>"]
        if filters.is_empty():
            summary_lines.append("No filters selected yet. Showing the full inventory.")
        else:
            summary_lines.append("Active filters:")
            if filters.price_min is not None or filters.price_max is not None:
                if filters.price_min and filters.price_max:
                    summary_lines.append(
                        f"- Budget between £{filters.price_min:,} and £{filters.price_max:,}."
                    )
                elif filters.price_min:
                    summary_lines.append(f"- Minimum budget £{filters.price_min:,}.")
                else:
                    summary_lines.append(f"- Maximum budget £{filters.price_max:,}.")
            if filters.seats_min:
                summary_lines.append(f"- Needs at least {filters.seats_min} seats.")
            if filters.max_mileage:
                summary_lines.append(f"- Keep mileage under {filters.max_mileage:,} miles.")
            if filters.min_year:
                summary_lines.append(f"- Model year {filters.min_year} or newer.")
            if filters.makes:
                summary_lines.append(f"- Preferred makes: {', '.join(filters.makes)}.")
            if filters.body_styles:
                summary_lines.append(f"- Body styles: {', '.join(filters.body_styles)}.")
            if filters.drivetrains:
                summary_lines.append(f"- Drivetrains: {', '.join(filters.drivetrains)}.")
            if filters.fuel_types:
                summary_lines.append(f"- Fuel types: {', '.join(filters.fuel_types)}.")
            if filters.locations:
                summary_lines.append(f"- Locations: {', '.join(filters.locations)}.")
            if filters.must_have_features:
                summary_lines.append(
                    f"- Must-have features: {', '.join(filters.must_have_features)}."
                )
        top_matches = ", ".join(car.display_name() for car in cars[:5]) or "No matches yet"
        summary_lines.append(f"Matches ready: {len(cars)} vehicles. Top picks: {top_matches}.")
        summary_lines.append("</CAR_SEARCH_PROFILE>")
        return "\n".join(summary_lines)

    def _resolve_matches(self, profile: CarSearchProfile) -> list[CarRecord]:
        return [
            self._inventory_by_id[car_id]
            for car_id in profile.match_ids
            if car_id in self._inventory_by_id
        ]

    def _apply_filters(self, filters: CarFilters) -> list[CarRecord]:
        def normalized(values: list[str]) -> set[str]:
            return {value.lower() for value in values}

        makes = normalized(filters.makes)
        body_styles = normalized(filters.body_styles)
        drivetrains = normalized(filters.drivetrains)
        fuel_types = normalized(filters.fuel_types)
        locations = normalized(filters.locations)
        features = normalized(filters.must_have_features)

        matches: list[CarRecord] = []
        for car in self._inventory:
            if filters.price_min is not None and car.price < filters.price_min:
                continue
            if filters.price_max is not None and car.price > filters.price_max:
                continue
            if filters.seats_min is not None and car.seats < filters.seats_min:
                continue
            if filters.max_mileage is not None and car.mileage > filters.max_mileage:
                continue
            if filters.min_year is not None and car.year < filters.min_year:
                continue
            if makes and car.make.lower() not in makes:
                continue
            if body_styles and car.body_style.lower() not in body_styles:
                continue
            if drivetrains and car.drivetrain.lower() not in drivetrains:
                continue
            if fuel_types and car.fuel_type.lower() not in fuel_types:
                continue
            if locations and car.location.lower() not in locations:
                continue
            if features:
                feature_blob = " ".join(car.features).lower()
                if any(feat not in feature_blob for feat in features):
                    continue
            matches.append(car)
        matches.sort(key=lambda c: (c.price, c.mileage))
        return matches


def load_inventory() -> CarInventoryStore:
    data_path = Path(__file__).parent / "data" / "cars.json"
    return CarInventoryStore(data_path)
