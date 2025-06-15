from datetime import date, timedelta
import pytest
import uuid

test_contact_data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "birthday": "1990-01-01",
    "additional_info": "123 Main St"
}


def test_create_contact(client, get_token):
    """Test creating a contact"""
    response = client.post(
        "/api/contacts",
        json=test_contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == test_contact_data["first_name"]
    assert data["last_name"] == test_contact_data["last_name"]
    assert data["email"] == test_contact_data["email"]
    assert data["phone"] == test_contact_data["phone"]
    assert data["birthday"] == test_contact_data["birthday"]
    assert data["additional_info"] == test_contact_data["additional_info"]
    assert "id" in data


def test_get_contact(client, get_token):
    """Test getting a contact"""
    response = client.get(
        "/api/contacts/1",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == test_contact_data["first_name"]
    assert data["last_name"] == test_contact_data["last_name"]
    assert data["email"] == test_contact_data["email"]
    assert "id" in data


def test_get_contact_not_found(client, get_token):
    """Test getting a contact that doesn't exist"""
    response = client.get(
        "/api/contacts/999",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contacts(client, get_token):
    """Test getting all contacts"""
    response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["first_name"] == test_contact_data["first_name"]
    assert "id" in data[0]


def test_update_contact(client, get_token):
    """Test updating a contact"""
    updated_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "phone": "0987654321",
        "birthday": "1995-05-05",
        "additional_info": "456 Oak St"
    }
    response = client.put(
        "/api/contacts/1",
        json=updated_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == updated_data["first_name"]
    assert data["last_name"] == updated_data["last_name"]
    assert data["email"] == updated_data["email"]
    assert data["phone"] == updated_data["phone"]
    assert data["birthday"] == updated_data["birthday"]
    assert data["additional_info"] == updated_data["additional_info"]
    assert "id" in data


def test_update_contact_not_found(client, get_token):
    """Test updating a contact that doesn't exist"""
    response = client.put(
        "/api/contacts/999",
        json={"first_name": "Jane"},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"

def test_delete_contact(client, get_token):
    """Test deleting a contact"""
    create_resp = client.post(
        "/api/contacts",
        json={
            "first_name": "ToDelete",
            "last_name": "User",
            "email": "todelete@example.com",
            "phone": "0000000000",
            "birthday": "2000-01-01",
            "additional_info": "For deletion"
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert create_resp.status_code == 201, create_resp.text
    contact_id = create_resp.json()["id"]

    delete_resp = client.delete(
        f"/api/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert delete_resp.status_code == 204, delete_resp.text


def test_delete_contact_not_found(client, get_token):
    """Test deleting a contact that doesn't exist"""
    response = client.delete(
        "/api/contacts/999",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_search_contacts(client, get_token):
    """Test searching for contacts"""
    unique_email = f"john_{uuid.uuid4().hex[:6]}@example.com"
    search_contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": unique_email,
        "phone": "1234567899",
        "birthday": "1990-01-01",
        "additional_info": "Search Street"
    }

    create_resp = client.post(
        "/api/contacts",
        json=search_contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert create_resp.status_code == 201, create_resp.text

    response = client.get(
        "/api/contacts/search/?query=John",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert any(c["email"] == unique_email for c in data)

@pytest.mark.skip(reason="Requires PostgreSQL for to_char function")
def test_get_upcoming_birthdays(client, get_token):
    """Test getting upcoming birthdays"""
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    upcoming_birthday_contact = {
        "first_name": "Birthday",
        "last_name": "Person",
        "email": "birthday@example.com",
        "phone": "1111111111",
        "birthday": tomorrow,
        "additional_info": "Birthday St"
    }
    client.post(
        "/api/contacts",
        json=upcoming_birthday_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )

    response = client.get(
        "/api/contacts/upcoming_birthdays/",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1
    assert data[0]["first_name"] == "Birthday"
    assert data[0]["last_name"] == "Person"
    assert data[0]["email"] == "birthday@example.com"
    assert data[0]["birthday"] == tomorrow 