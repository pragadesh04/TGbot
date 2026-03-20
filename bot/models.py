from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Course:
    title: str
    description: str
    fee: float
    image_url: str
    registration_count: int = 0
    _id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Registration:
    telegram_id: int
    name: str
    address: str
    course_id: str
    course_title: str
    amount: float
    screenshot_url: Optional[str] = None
    status: str = "pending"
    _id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ChatMessage:
    telegram_id: int
    role: str
    message: str
    created_at: Optional[datetime] = None
