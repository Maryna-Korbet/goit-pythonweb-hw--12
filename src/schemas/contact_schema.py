from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from src.config import messages
from src.config import constants


class ContactSchema(BaseModel):
    """Contact schema for creating a new contact."""
    id: int
    first_name: str = Field(
        min_length=constants.FIRST_NAME_MIN_LENGTH, 
        max_length=constants.FIRST_NAME_MAX_LENGTH,
        description=messages.contact_schema_first_name.get("en")
    )
    last_name: str = Field(
        min_length=constants.LAST_NAME_MIN_LENGTH, 
        max_length=constants.LAST_NAME_MAX_LENGTH,
        description=messages.contact_schema_last_name.get("en")
    )
    email: str = Field(
        min_length=constants.EMAIL_MIN_LENGTH, 
        max_length=constants.EMAIL_MAX_LENGTH,
        description=messages.contact_schema_email.get("en")
    )
    phone: Optional[str] = Field(
        min_length=constants.PHONE_MIN_LENGTH, 
        max_length=constants.PHONE_MAX_LENGTH,
        description=messages.contact_schema_phone.get("en")
    )
    birthday: date = Field(
        default=None, 
        description=messages.contact_birthday_description.get("en")
    )
    additional_info: str = Field(
        default=None, 
        max_length=constants.ADDITIONAL_INFO_MAX_LENGTH,
        description=messages.contact_additional_info_description.get("en")
    )


class ContactUpdateSchema(BaseModel):
    """Contact schema for updating a contact."""
    id: int
    first_name: str = Field(
        min_length=constants.FIRST_NAME_MIN_LENGTH, 
        max_length=constants.FIRST_NAME_MAX_LENGTH,
        description=messages.contact_schema_first_name.get("en")
    )
    last_name: str = Field(
        min_length=constants.LAST_NAME_MIN_LENGTH, 
        max_length=constants.LAST_NAME_MAX_LENGTH,
        description=messages.contact_schema_last_name.get("en")
    )
    email: str = Field(
        min_length=constants.EMAIL_MIN_LENGTH, 
        max_length=constants.EMAIL_MAX_LENGTH,
        description=messages.contact_schema_email.get("en")
    )
    phone: Optional[str] = Field(
        min_length=constants.PHONE_MIN_LENGTH, 
        max_length=constants.PHONE_MAX_LENGTH,
        description=messages.contact_schema_phone.get("en")
    )
    birthday: date = Field(
        default=None, 
        description=messages.contact_birthday_description.get("en")
    )
    additional_info: str = Field(
        default=None, 
        max_length=constants.ADDITIONAL_INFO_MAX_LENGTH,
        description=messages.contact_additional_info_description.get("en")
    )


class ContactResponse(BaseModel):
    """Contact response schema."""
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]    
    birthday: date    
    additional_info: str   
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)