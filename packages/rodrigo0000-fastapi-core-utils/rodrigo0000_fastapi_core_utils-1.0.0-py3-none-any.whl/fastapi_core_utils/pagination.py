"""
Pagination utilities
"""

from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    size: int = 10

class PaginatedResult(BaseModel, Generic[T]):
    """Paginated result container"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    hasPrev: bool
    hasNext: bool
