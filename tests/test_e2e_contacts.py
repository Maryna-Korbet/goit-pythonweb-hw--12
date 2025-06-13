from datetime import date, timedelta
import pytest

# data ==================================
contact_data = {
    "first_name": "Alice",
    "last_name": "Johnson",
    "email": "alice.johnson@example.com",
    "phone_number": "5551234567",
    "birthday": "1988-12-12",
    "additional_info": "789 Sunset Blvd"
}

updated_contact_data = {
    "first_name": "Bob",
    "last_name": "Williams",
    "email": "bob.williams@example.com",
    "phone_number": "7778889999",
    "birthday": "1992-07-20",
    "additional_info": "321 Ocean Drive"
}

upcoming_contact_data = {
    "first_name": "Clara",
    "last_name": "White",
    "email": "clara.white@example.com",
    "phone_number": "4445556666",
    "birthday": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
    "additional_info": "555 Birthday Ln"
}


# tests================================
def test_create_contact(client, get_token):
    """Test create contact endpoint."""
    response = client.post(
        "/api/contacts",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    for key in contact_data:
        assert data[key] == contact_data[key]
    assert "id" in data


def test_get_contact(client, get_token):
    """Test get contact endpoint."""
    response = client.get(
        "/api/contacts/1",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == contact_data["first_name"]
    assert data["last_name"] == contact_data["last_name"]
    assert data["email"] == contact_data["email"]
    assert "id" in data


def test_get_contact_not_found(client, get_token):
    """Test get contact endpoint."""
    response = client.get(
        "/api/contacts/999",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Контакт не знайдено"


def test_get_contacts(client, get_token):
    """Test get contacts endpoint."""
    response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["first_name"] == contact_data["first_name"]
    assert "id" in data[0]


def test_update_contact(client, get_token):
    """Test update contact endpoint."""
    response = client.put(
        "/api/contacts/1",
        json=updated_contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    for key in updated_contact_data:
        assert data[key] == updated_contact_data[key]
    assert "id" in data


def test_update_contact_not_found(client, get_token):
    """Test update contact endpoint."""
    response = client.put(
        "/api/contacts/999",
        json={"first_name": "Ghost"},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Контакт не знайдено"


def test_delete_contact(client, get_token):
    """Test delete contact endpoint."""
    response = client.delete(
        "/api/contacts/1",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 204, response.text


def test_delete_contact_not_found(client, get_token):
    """Test delete contact endpoint."""
    response = client.delete(
        "/api/contacts/999",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Контакт не знайдено"


def test_search_contacts(client, get_token):
    """Test search contacts endpoint."""
    client.post(
        "/api/contacts",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    response = client.get(
        "/api/contacts/search/?query=Alice",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["first_name"] == contact_data["first_name"]


@pytest.mark.skip(reason="Requires PostgreSQL for to_char function")
def test_get_upcoming_birthdays(client, get_token):
    """Test get upcoming birthdays endpoint."""
    client.post(
        "/api/contacts",
        json=upcoming_contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    response = client.get(
        "/api/contacts/upcoming_birthdays/",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1
    assert data[0]["first_name"] == upcoming_contact_data["first_name"]
    assert data[0]["last_name"] == upcoming_contact_data["last_name"]
    assert data[0]["email"] == upcoming_contact_data["email"]
    assert data[0]["birthday"] == upcoming_contact_data["birthday"]