from fastapi import APIRouter, Depends, HTTPException, status
from app.database import notes_collection
from app.utils.auth_utils import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post(
    "/",
    summary="Create a new note",
    description="""
Create a new note associated with the currently authenticated user.  
The note data (like title and content) should be passed in the request body.
""",
    response_description="Confirmation message with created note ID",
    responses={
        200: {
            "description": "Note created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "64f27e8db4c2f35a50c8b12a",
                        "message": "Note created.",
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized - invalid or missing token",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    },
)
def create_note(note: dict, current_user: dict = Depends(get_current_user)):
    note["user"] = str(current_user["email"])
    result = notes_collection.insert_one(note)
    return {"id": str(result.inserted_id), "message": "Note created."}


@router.get(
    "/",
    summary="Get all notes of the logged-in user",
    description="""
Fetch all notes created by the currently authenticated user.  
Returns a list of note objects with their details.
""",
    response_description="List of notes belonging to the user",
    responses={
        200: {
            "description": "Successfully retrieved all notes",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "_id": "64f27e8db4c2f35a50c8b12a",
                            "title": "Shopping List",
                            "content": "Buy milk, eggs, bread",
                            "user": "john@example.com",
                        },
                        {
                            "_id": "64f27e8db4c2f35a50c8b12b",
                            "title": "Work Notes",
                            "content": "Prepare demo slides",
                            "user": "john@example.com",
                        },
                    ]
                }
            },
        },
        401: {
            "description": "Unauthorized - invalid or missing token",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    },
)
def get_my_notes(current_user: dict = Depends(get_current_user)):
    notes = list(notes_collection.find({"user": current_user["email"]}))
    for note in notes:
        note["_id"] = str(note["_id"])
    return notes


@router.put(
    "/{note_id}",
    summary="Update an existing note",
    description="""
Update a note by its ID.  
Only the owner of the note can modify it.  
Pass the updated fields (e.g., title, content) in the request body.
""",
    response_description="Confirmation message after update",
    responses={
        200: {
            "description": "Note updated successfully",
            "content": {"application/json": {"example": {"message": "Note updated."}}},
        },
        404: {
            "description": "Note not found or not owned by user",
            "content": {
                "application/json": {
                    "example": {"detail": "Note cannot be modified by you."}
                }
            },
        },
    },
)
def update_note(
    note_id: str, note: dict, current_user: dict = Depends(get_current_user)
):
    result = notes_collection.update_one(
        {"_id": ObjectId(note_id), "user": str(current_user["email"])}, {"$set": note}
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note cannot be modified by you.",
        )
    return {"message": "Note updated."}


@router.delete(
    "/{note_id}",
    summary="Delete a note",
    description="""
Delete a specific note by its ID.  
Only the owner of the note can delete it.
""",
    response_description="Confirmation message after deletion",
    responses={
        200: {
            "description": "Note deleted successfully",
            "content": {"application/json": {"example": {"message": "Note deleted."}}},
        },
        404: {
            "description": "Note not found or not owned by user",
            "content": {
                "application/json": {
                    "example": {"detail": "Note cannot be deleted by you."}
                }
            },
        },
    },
)
def delete_note(note_id: str, current_user: dict = Depends(get_current_user)):
    result = notes_collection.delete_one(
        {"_id": ObjectId(note_id), "user": str(current_user["email"])}
    )
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note cannot be deleted by you.",
        )
    return {"message": "Note deleted."}
