from typing import Optional

from pydantic import BaseModel


class SearchResult(BaseModel):
    url: str
    title: str
    headline: Optional[str] = None


class SearchRequest(BaseModel):
    query: str