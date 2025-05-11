from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.contacts_repository import ContactRepository
from src.schemas.contact_schema import ContactSchema, ContactUpdateSchema
from src.entity.models import User


class ContactService:
    """Contact service."""
    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)

    async def get_contacts(self, limit: int, offset: int, user: User):
        """Get a list of contacts."""
        return await self.contact_repository.get_contacts(limit, offset, user)

    async def get_contact(self, contact_id: int, user: User):
        """Get a contact by ID."""
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def create_contact(self, body: ContactSchema, user: User):
        """Create a new contact."""
        return await self.contact_repository.create_contact(body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """Remove a contact by ID."""
        return await self.contact_repository.remove_contact(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdateSchema, user: User):
        """Update a contact by ID."""
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def search_contacts(self, query: str, user: User):
        """Search for contacts by query."""
        return await self.contact_repository.search_contacts(query, user)

    async def upcoming_birthdays(self, user: User):
        """Get contacts with upcoming birthdays."""
        today = date.today()
        end_date = today + timedelta(days=7)
        return await self.contact_repository.get_contacts_with_birthdays(today, end_date, user)