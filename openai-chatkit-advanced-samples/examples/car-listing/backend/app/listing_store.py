from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

REQUIRED_FIELDS: List[str] = [
    "seller_name",
    "contact_email",
    "contact_phone",
    "make",
    "model",
    "year",
    "trim",
    "body_style",
    "fuel_type",
    "transmission",
    "drivetrain",
    "color",
    "mileage",
    "asking_price",
    "location",
    "mot_expiry",
    "service_history",
    "description",
    "key_features",
    "photo_urls",
]

LIST_FIELDS = {"key_features", "photo_urls"}


@dataclass
class ListingRecord:
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
    key_features: list[str] = field(default_factory=list)
    photo_urls: list[str] = field(default_factory=list)
    status: str = "draft"
    submitted_at: datetime | None = None
    title: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "seller_name": self.seller_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "trim": self.trim,
            "body_style": self.body_style,
            "fuel_type": self.fuel_type,
            "transmission": self.transmission,
            "drivetrain": self.drivetrain,
            "color": self.color,
            "mileage": self.mileage,
            "asking_price": self.asking_price,
            "location": self.location,
            "mot_expiry": self.mot_expiry,
            "service_history": self.service_history,
            "description": self.description,
            "key_features": list(self.key_features),
            "photo_urls": list(self.photo_urls),
            "status": self.status,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
        }


class ListingStore:
    def __init__(self) -> None:
        self._records: Dict[str, ListingRecord] = {}

    def get(self, thread_id: str) -> ListingRecord:
        if thread_id not in self._records:
            self._records[thread_id] = ListingRecord()
        return self._records[thread_id]

    def snapshot(self, thread_id: str | None) -> dict[str, Any]:
        record = self.get(thread_id or self._default_thread_id())
        missing = self.missing_fields(record)
        return {
            "fields": record.to_payload(),
            "missing_fields": missing,
            "completed": len(missing) == 0,
        }

    def update(self, thread_id: str, updates: dict[str, Any]) -> ListingRecord:
        record = self.get(thread_id)
        for key, value in updates.items():
            if value is None:
                continue
            if key in LIST_FIELDS:
                if isinstance(value, list):
                    setattr(record, key, [str(item).strip() for item in value if str(item).strip()])
                elif isinstance(value, str):
                    setattr(record, key, [segment.strip() for segment in value.split(",") if segment.strip()])
                else:
                    continue
            elif hasattr(record, key):
                setattr(record, key, value)
        self._sync_title(record)
        if record.status == "submitted":
            record.status = "draft"
            record.submitted_at = None
        return record

    def submit(self, thread_id: str) -> ListingRecord:
        record = self.get(thread_id)
        missing = self.missing_fields(record)
        if missing:
            raise ValueError(f"Cannot submit listing; missing fields: {', '.join(missing)}")
        record.status = "submitted"
        record.submitted_at = datetime.utcnow()
        return record

    def reset(self, thread_id: str) -> ListingRecord:
        self._records[thread_id] = ListingRecord()
        return self._records[thread_id]

    def missing_fields(self, record: ListingRecord) -> list[str]:
        missing: list[str] = []
        for field_name in REQUIRED_FIELDS:
            value = getattr(record, field_name, None)
            if field_name in LIST_FIELDS:
                if not value:
                    missing.append(field_name)
            elif value in (None, "", []):
                missing.append(field_name)
        return missing

    def build_context_block(self, thread_id: str) -> str:
        record = self.get(thread_id)
        missing = self.missing_fields(record)
        lines = ["<CURRENT_LISTING>"]
        lines.append(f"Status: {record.status}")
        if record.status == "submitted":
            lines.append(f"Submitted at: {record.submitted_at.isoformat() if record.submitted_at else 'pending'}")
        lines.append("Missing fields: " + (", ".join(missing) if missing else "None, everything captured."))
        lines.append("Entered fields:")
        for field_name in REQUIRED_FIELDS:
            value = getattr(record, field_name, None)
            if field_name in LIST_FIELDS:
                display = ", ".join(value) if value else "—"
            else:
                display = str(value) if value not in (None, "") else "—"
            lines.append(f"- {field_name.replace('_', ' ').title()}: {display}")
        lines.append("</CURRENT_LISTING>")
        return "\n".join(lines)

    def _default_thread_id(self) -> str:
        if "__default__" not in self._records:
            self._records["__default__"] = ListingRecord()
        return "__default__"

    def _sync_title(self, record: ListingRecord) -> None:
        if record.year and record.make and record.model:
            record.title = f"{record.year} {record.make} {record.model}"
        elif record.make and record.model:
            record.title = f"{record.make} {record.model}"
        else:
            record.title = None
