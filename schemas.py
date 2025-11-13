"""
Database Schemas for Nova — a clean social platform with channels (Discord-like),
short videos (Instagram-like), and an AI chatbot.

Each Pydantic model maps to a MongoDB collection using the lowercase class name.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List


class User(BaseModel):
    """
    Users collection schema
    Collection name: "user"
    """
    username: str = Field(..., min_length=3, max_length=32, description="Unique handle")
    display_name: Optional[str] = Field(None, max_length=64, description="Profile display name")
    avatar_url: Optional[HttpUrl] = Field(None, description="Profile avatar URL")
    bio: Optional[str] = Field(None, max_length=280, description="Short bio")
    is_active: bool = Field(True, description="Whether user is active")


class Channel(BaseModel):
    """
    Channels for realtime chat (Discord-like)
    Collection name: "channel"
    """
    name: str = Field(..., min_length=2, max_length=64, description="Channel name")
    topic: Optional[str] = Field(None, max_length=140, description="Channel topic/description")
    is_private: bool = Field(False, description="If true, channel is private")


class Message(BaseModel):
    """
    Chat messages inside channels
    Collection name: "message"
    """
    channel_id: str = Field(..., description="Target channel id (string)")
    author: str = Field(..., min_length=3, max_length=32, description="Username of author")
    content: str = Field(..., min_length=1, max_length=4000, description="Message content")


class Video(BaseModel):
    """
    Short video posts (Instagram-like). For demo, store remote URL and metadata.
    Collection name: "video"
    """
    author: str = Field(..., min_length=3, max_length=32, description="Username of author")
    caption: Optional[str] = Field(None, max_length=300, description="Caption text")
    video_url: HttpUrl = Field(..., description="Publicly accessible video URL")
    thumbnail_url: Optional[HttpUrl] = Field(None, description="Optional thumbnail URL")
    likes: int = Field(0, ge=0, description="Like counter")
    tags: List[str] = Field(default_factory=list, description="Hashtags or labels")


class BotMessage(BaseModel):
    """
    AI chatbot message request
    Collection name: "botmessage"
    """
    user: str = Field(..., min_length=3, max_length=32, description="Username of the user")
    message: str = Field(..., min_length=1, max_length=4000, description="User message for the AI bot")
