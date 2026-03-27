import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import APIRouter, HTTPException
from typing import List, Optional
import database
import models
from models import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    RegistrationResponse,
    StatsResponse,
    ConfigUpdate,
)
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["admin"])


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    return await database.get_stats()


@router.get("/courses", response_model=List[CourseResponse])
async def list_courses():
    return await database.get_courses()


@router.post("/courses", response_model=dict)
async def create_course(course: CourseCreate):
    course_dict = course.model_dump()
    if not course_dict.get("image_url"):
        course_dict["image_url"] = (
            f"https://placehold.co/400x200/transparent/white?text={course_dict['title'].replace(' ', '+')}&font=Poppins"
        )
    course_id = await database.create_course(course_dict)
    return {"id": course_id, "message": "Course created successfully"}


@router.put("/courses/{course_id}")
async def update_course(course_id: str, course: CourseUpdate):
    existing = await database.get_course_by_id(course_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Course not found")

    update_data = course.model_dump(exclude_unset=True)
    if update_data.get("image_url") == "":
        update_data["image_url"] = None
    await database.update_course(course_id, update_data)
    return {"message": "Course updated successfully"}


@router.delete("/courses/{course_id}")
async def delete_course(course_id: str):
    existing = await database.get_course_by_id(course_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Course not found")

    await database.delete_course(course_id)
    return {"message": "Course deleted successfully"}


@router.put("/courses/{course_id}/toggle-registration")
async def toggle_course_registration(course_id: str):
    """Toggle registration open/closed status for a course"""
    existing = await database.get_course_by_id(course_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Course not found")

    current_status = existing.get("registration_open", True)
    new_status = not current_status
    await database.update_course(course_id, {"registration_open": new_status})
    status_text = "opened" if new_status else "closed"
    return {
        "message": f"Registration {status_text} successfully",
        "registration_open": new_status,
    }


@router.get("/registrations", response_model=List[RegistrationResponse])
async def list_registrations(
    status: Optional[str] = None,
    course: Optional[str] = None,
    sort_by: Optional[str] = None,
    order: Optional[str] = "desc",
):
    return await database.get_registrations(status, course, sort_by, order)


@router.get("/registrations/{registration_id}", response_model=RegistrationResponse)
async def get_registration(registration_id: str):
    reg = await database.get_registration_by_id(registration_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    return reg


@router.put("/registrations/{registration_id}/approve")
async def approve_registration(registration_id: str):
    reg = await database.get_registration_by_id(registration_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")

    await database.update_registration_status(registration_id, "approved")

    if reg.get("course_id"):
        await database.increment_course_count(reg["course_id"])

    return {"message": "Registration approved successfully"}


@router.put("/registrations/{registration_id}/reject")
async def reject_registration(registration_id: str, reason: str = None):
    reg = await database.get_registration_by_id(registration_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")

    await database.update_registration_status(registration_id, "rejected", reason)
    return {"message": "Registration rejected"}


@router.get("/config/upi")
async def get_upi():
    value = await database.get_config("upi_id")
    return {"upi_id": value or "yourname@upi"}


@router.put("/config/upi")
async def update_upi(config: ConfigUpdate):
    await database.set_config("upi_id", config.value)
    return {"message": "UPI ID updated successfully"}
