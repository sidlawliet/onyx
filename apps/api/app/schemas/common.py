from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number starting from 1")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)


class ApiMessage(BaseModel):
    message: str
    status: str = "success"


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | None = None
