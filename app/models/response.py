from typing import Any
from pydantic import BaseModel, Field

class FieldResponse(BaseModel):
    value: Any | None
    confidence: float = Field(ge=0.0, le=1.0)

class LineItemResponse(BaseModel):
    description: str
    quantity: float | None
    unit_price: float | None
    line_total: float | None
    confidence: float = Field(ge=0.0, le=1.0)

class ValidationIssueResponse(BaseModel):
    code: str
    message: str
    severity: str
    field: str | None = None

class DocumentAnalysisResponse(BaseModel):
    document_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    fields: dict[str, FieldResponse]
    line_items: list[LineItemResponse]
    validation_issues: list[ValidationIssueResponse]
    status: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str