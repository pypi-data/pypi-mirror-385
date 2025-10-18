# This is free and unencumbered software released into the public domain.

from pydantic import BaseModel, Field
from typing import Any, Optional


class Percept(BaseModel):
    type: str = Field("Percept", alias="@type")
    id: str = Field(..., alias="@id")

    def to_json(self) -> str:
        import json

        return json.dumps(self.to_dict(), separators=(",", ":"))

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_computed_fields=True)


class VisualPercept(Percept):
    type: str = Field("VisualPercept", alias="@type")
    source: Optional[str] = None
    subject: str
    confidence: float
