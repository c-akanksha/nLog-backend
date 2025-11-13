from fastapi import FastAPI
from app.routes import auth, notes

app = FastAPI(
    title="nLog app",
    description="A secure and simple **Notes Management API** built with FastAPI and MongoDB."
    "It allows users to **sign up, login and manage their notes**"
    "Each user can access only their own notes."
    "JWT-based authentication ensures secure access",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(notes.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "nLog is up and running!"}
