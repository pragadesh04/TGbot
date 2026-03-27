from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CourseBase(BaseModel):
    title: str
    description: str
    fee: float
    image_url: Optional[str] = None
    course_type: str = "recorded"
    start_date: Optional[str] = None
    start_time: Optional[str] = None
    sessions: Optional[int] = None
    duration: Optional[float] = None
    registration_open: bool = True


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    fee: Optional[float] = None
    image_url: Optional[str] = None
    course_type: Optional[str] = None
    start_date: Optional[str] = None
    start_time: Optional[str] = None
    sessions: Optional[int] = None
    duration: Optional[float] = None
    registration_open: Optional[bool] = None


class CourseResponse(CourseBase):
    id: str
    _id: str
    registration_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RegistrationResponse(BaseModel):
    id: str
    telegram_id: int
    name: str
    address: str
    mobile: Optional[str] = None
    course_id: Optional[str] = None
    course_title: str
    amount: float
    screenshot_url: Optional[str] = None
    status: str
    rejection_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int


class ConfigUpdate(BaseModel):
    value: str
