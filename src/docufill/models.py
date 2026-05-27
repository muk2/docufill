"""Data models for extracted document fields."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class DocumentResult:
    """Structured result from document scanning."""

    surname: Optional[str] = None
    given_names: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    sex: Optional[str] = None
    nationality: Optional[str] = None
    document_number: Optional[str] = None
    expiry_date: Optional[str] = None
    document_type: Optional[str] = None
    issuing_country: Optional[str] = None
    personal_number: Optional[str] = None
    method: Optional[str] = None
    extras: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None and v != {}}

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_table(self) -> str:
        lines = []
        for key, value in self.to_dict().items():
            if key == "extras":
                for ek, ev in value.items():
                    label = ek.replace("_", " ").title()
                    lines.append(f"  {label:<22} {ev}")
            else:
                label = key.replace("_", " ").title()
                lines.append(f"  {label:<22} {value}")
        return "\n".join(lines)
