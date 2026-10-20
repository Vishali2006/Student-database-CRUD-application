"""Pydantic models for student request and response data."""

import re
from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class StudentFields(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=30)
    course: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=250)
    enrollment_date: date | None = None

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("phone", "course", "address", mode="before")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip() or None
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is not None:
            if not re.fullmatch(r"[0-9+().\-\s]{7,30}", value) or not any(
                character.isdigit() for character in value
            ):
                raise ValueError("Enter a valid phone number.")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return value

    @model_validator(mode="after")
    def require_contact_method(self) -> "StudentFields":
        if self.email is None and self.phone is None:
            raise ValueError("Provide at least an email address or phone number.")
        return self


class StudentCreate(StudentFields):
    """Fields accepted when registering a student."""


class StudentUpdate(StudentFields):
    """Complete set of fields required to replace a student record."""


class StudentResponse(StudentFields):
    """Student data returned by the API."""

    id: int
