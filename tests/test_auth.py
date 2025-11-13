from fastapi import status


def test_signup_success(client, mock_db):
    notes_collection, users_collection = mock_db
    users_collection.find_one.return_value = None  # No existing user

    response = client.post(
        "/auth/signup",
        params={"name": "John", "email": "john@example.com", "password": "hashed_pwd"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "User created successfully"}


def test_signup_existing_email(client, mock_db):
    _, users_collection = mock_db
    users_collection.find_one.return_value = {"email": "john@example.com"}

    response = client.post(
        "/auth/signup",
        params={"name": "John", "email": "john@example.com", "password": "hashed_pwd"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already exists"


def test_login_success(client, mock_db, mocker):
    _, users_collection = mock_db
    users_collection.find_one.return_value = {
        "email": "john@example.com",
        "password": "hashed_pwd",
    }

    mocker.patch("app.routes.auth.verify_password", return_value=True)
    mocker.patch("app.routes.auth.create_access_token", return_value="mock_token")

    response = client.post(
        "/auth/login", data={"username": "john@example.com", "password": "hashed_pwd"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["access_token"] == "mock_token"
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, mock_db, mocker):
    _, users_collection = mock_db
    users_collection.find_one.return_value = None

    response = client.post(
        "/auth/login", data={"username": "wrong@example.com", "password": "hashed_pwd"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"
