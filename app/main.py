from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, notes

app = FastAPI(
    title="nLog app",
    description="A secure and simple **Notes Management API** built with FastAPI and MongoDB."
    "It allows users to **sign up, login and manage their notes**"
    "Each user can access only their own notes."
    "JWT-based authentication ensures secure access",
    version="1.0.0",
)

origins = [
    # Local development
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    # GitHub Pages
    "https://c-akanksha.github.io",
    "https://c-akanksha.github.io/nLog",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(notes.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "nLog is up and running!"}
