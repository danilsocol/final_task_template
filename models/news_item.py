from typing import List

from pydantic import BaseModel


class NewsItem(BaseModel):
    title: str
    date: str
    relate_image_link: str
    description: str