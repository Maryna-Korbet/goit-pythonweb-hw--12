import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.contact_services import ContactService
from src.schemas.contact_schema import (
    ContactSchema, 
    ContactResponse, 
    ContactUpdateSchema
    )
from src.config import messages
from src.core.depend_service import get_current_user
from src.entity.models import User


router = APIRouter(prefix="/contacts", tags=["contacts"])
logger = logging.getLogger("uvicorn.error")


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(
    limit: int = Query(10, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get a list of contacts.

    Args:
        limit (int): The maximum number of contacts to retrieve.
        offset (int): The number of contacts to skip.
        db (AsyncSession): The database session dependency.

    Returns:
        list[ContactResponse]: A list of contacts.
    """
    contact_service = ContactService(db)
    return await contact_service.get_contacts(limit, offset, user)


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    name="Get contact by id",
    description="Description of the endpoint",
    response_description="Response description",
)
async def get_contact(
    contact_id: int, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get a contact by ID.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The database session dependency.

    Returns:
        ContactResponse: The retrieved contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.contact_not_found.get("ua"),
        )
    return contact


@router.get(
    "/search/",
    response_model=list[ContactResponse],
    description=messages.contact_search_description.get("ua"),
)
async def search_contacts(
    query: str = Query(
        ..., 
        min_length=1, 
        max_length=100, 
        example="John Doe", 
        description=messages.contact_search_description.get("ua")
        ),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Search contacts by name, last name, or email.

    Args:
        query (str): The search query.
        db (AsyncSession): The database session dependency.

    Returns:
        list[ContactResponse]: A list of contacts that match the search query.
    """
    contact_service = ContactService(db)
    return await contact_service.search_contacts(query, user)


@router.get(
    "/upcoming_birthdays/",
    response_model=list[ContactResponse],
    description="Retrieve contacts with birthdays in the next 7 days.",
)
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Retrieve contacts who have birthdays within the next 7 days.

    Args:
        db (AsyncSession): The database session dependency.

    Returns:
        list[ContactResponse]: A list of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    return await contact_service.upcoming_birthdays(user)


@router.post(
        "/", 
        response_model=ContactResponse, 
        status_code=status.HTTP_201_CREATED
        )
async def create_contact(
    body: ContactSchema, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Create a new contact.

    Args:
        body (ContactSchema): The contact data.
        db (AsyncSession): The database session dependency.

    Returns:
        ContactResponse: The created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int, 
    body: ContactUpdateSchema, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Update a contact by ID.

    Args:
        contact_id (int): The ID of the contact to update.
        body (ContactUpdateSchema): The updated contact data.
        db (AsyncSession): The database session dependency.

    Returns:
        ContactResponse: The updated contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.contact_not_found.get("ua"),
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int, 
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """
    Delete a contact by ID.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): The database session dependency.

    Returns:
        None
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.contact_not_found.get("ua"),
        )
    return None