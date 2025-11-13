from fastapi import status
from unittest import mock
from app.routes import notes as notes_route


def test_create_note_success(client, mock_db):
    notes_collection, _ = mock_db
    # Configure the mock to return a fake inserted_id
    fake_result = type("R", (), {"inserted_id": "mock_id"})()
    notes_collection.insert_one.return_value = fake_result

    # override the dependency the *app* actually uses
    client.app.dependency_overrides[notes_route.get_current_user] = lambda: {
        "email": "john@example.com"
    }

    response = client.post(
        "/notes/",
        json={"title": "Test Note", "content": "Hello world"},
        headers={"Authorization": "Bearer fake-token-for-tests"},
    )

    # cleanup: remove override
    client.app.dependency_overrides.pop(notes_route.get_current_user, None)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {"id": "mock_id", "message": "Note created."}


def test_get_my_notes(client, mock_db, mock_token):
    notes_collection, _ = mock_db
    mock_notes = [
        {
            "_id": "1",
            "title": "Note 1",
            "content": "Text 1",
            "user": "john@example.com",
        },
        {
            "_id": "2",
            "title": "Note 2",
            "content": "Text 2",
            "user": "john@example.com",
        },
    ]
    notes_collection.find.return_value = mock_notes

    # --- 👇 override dependency here 👇
    client.app.dependency_overrides[notes_route.get_current_user] = lambda: {
        "email": "john@example.com"
    }

    response = client.get("/notes/", headers={"Authorization": f"Bearer {mock_token}"})

    # Clean up
    client.app.dependency_overrides.pop(notes_route.get_current_user, None)

    # --- Assertions ---
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Note 1"


def test_update_note_success(client, mock_db, mock_token):
    notes_collection, _ = mock_db
    notes_collection.update_one.return_value.matched_count = 1

    # Override dependency for authentication
    client.app.dependency_overrides[notes_route.get_current_user] = lambda: {
        "email": "john@example.com"
    }

    with mock.patch("app.routes.notes.ObjectId", return_value="mock_object_id"):
        response = client.put(
            "/notes/123",
            json={"title": "Updated Title"},
            headers={"Authorization": f"Bearer {mock_token}"},
        )

    # Clean up override
    client.app.dependency_overrides.pop(notes_route.get_current_user, None)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Note updated."}


def test_update_note_not_owned(client, mock_db, mock_token):
    notes_collection, _ = mock_db
    notes_collection.update_one.return_value.matched_count = 0

    # ✅ Override the authentication dependency
    client.app.dependency_overrides[notes_route.get_current_user] = lambda: {
        "email": "john@example.com"
    }

    # ✅ Patch ObjectId to bypass BSON validation
    with mock.patch("app.routes.notes.ObjectId", return_value="mock_object_id"):
        response = client.put(
            "/notes/999",
            json={"title": "Hacked"},
            headers={"Authorization": f"Bearer {mock_token}"},
        )

    # Cleanup after test
    client.app.dependency_overrides.pop(notes_route.get_current_user, None)

    # ✅ Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert response.json()["detail"] == "Note cannot be modified by you."


def test_delete_note_success(client, mock_db, mock_token):
    notes_collection, _ = mock_db
    notes_collection.delete_one.return_value.deleted_count = 1

    # Override auth dependency
    client.app.dependency_overrides[notes_route.get_current_user] = lambda: {
        "email": "john@example.com"
    }

    # Patch ObjectId to bypass validation
    with mock.patch("app.routes.notes.ObjectId", return_value="mock_object_id"):
        response = client.delete(
            "/notes/123", headers={"Authorization": f"Bearer {mock_token}"}
        )

    # Clean up override
    client.app.dependency_overrides.pop(notes_route.get_current_user, None)

    # Assertions
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {"message": "Note deleted."}
