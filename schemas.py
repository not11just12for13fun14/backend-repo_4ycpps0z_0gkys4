"""
Database Schemas for Theatre Studio Nepal

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl


class Event(BaseModel):
    """
    Theatre events (performances, workshops, festivals)
    Collection: "event"
    """
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Short description")
    date: str = Field(..., description="ISO date string (e.g., 2025-01-31)")
    venue: Optional[str] = Field(None, description="Venue name")
    city: Optional[str] = Field(None, description="City")
    country: Optional[str] = Field("Nepal", description="Country")
    status: Literal["live", "upcoming", "past"] = Field(
        "upcoming", description="Event status"
    )
    cover_image: Optional[HttpUrl] = Field(None, description="Cover image URL")
    tags: List[str] = Field(default_factory=list, description="Tags/genres")


class Publication(BaseModel):
    """
    Publications (books, research papers, articles)
    Collection: "publication"
    """
    title: str
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    link: Optional[HttpUrl] = None
    cover_image: Optional[HttpUrl] = None
    summary: Optional[str] = None


class Work(BaseModel):
    """
    Original works/productions
    Collection: "work"
    """
    title: str
    year: Optional[int] = None
    type: Literal["play", "production", "workshop", "festival", "other"] = "play"
    description: Optional[str] = None
    images: List[HttpUrl] = Field(default_factory=list)


class Galleryitem(BaseModel):
    """
    Gallery assets
    Collection: "galleryitem"
    """
    title: str
    image_url: HttpUrl
    category: Optional[str] = None
    taken_at: Optional[str] = Field(None, description="ISO date string")


# Note: The Flames database viewer can introspect these at /schema
