from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.database import users_collection
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


class User(BaseModel):
    name: str
    email: str
    password: str


@router.post(
    "/signup",
    summary="Create a new user account",
    description="""
Register a new user by providing their **name**, **email**, and **password**.  
If the provided email already exists in the system, the request will fail with an error.
""",
    response_description="Confirmation message after successful signup",
    responses={
        200: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {"message": "User created successfully"}
                }
            },
        },
        400: {
            "description": "Email already exists",
            "content": {
                "application/json": {"example": {"detail": "Email already exists"}}
            },
        },
    },
)
def signup(user: User):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )
    users_collection.insert_one(
        {
            "name": user.name,
            "email": user.email,
            "password": hash_password(user.password),
        }
    )
    return {"message": "User created successfully"}


@router.post(
    "/login",
    summary="Authenticate and get access token",
    description="""
Logs in a user using their **email** and **password**.  
If the credentials are valid, returns a **JWT access token** that can be used to authenticate subsequent requests.
""",
    response_description="JWT token response",
    responses={
        200: {
            "description": "Login successful - JWT token returned",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {"example": {"detail": "Invalid credentials"}}
            },
        },
    },
)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"email": form_data.username})
    print(f"user: {user}")
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}
