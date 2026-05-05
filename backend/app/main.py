from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.config import settings
from app.routers import auth, users, profile, courses, attendance, finance, payments, analytics
from app.database import create_tables

# Make sure tables are created
create_tables()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# Set all CORS enabled origins
if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["users"])
app.include_router(profile.router, prefix=f"{settings.API_PREFIX}/profile", tags=["profile"])
app.include_router(courses.router, prefix=f"{settings.API_PREFIX}/courses", tags=["courses"])
app.include_router(attendance.router, prefix=f"{settings.API_PREFIX}/attendance", tags=["attendance"])
app.include_router(finance.router, prefix=f"{settings.API_PREFIX}/finance", tags=["finance"])
app.include_router(payments.router, prefix=f"{settings.API_PREFIX}/payments", tags=["payments"])
app.include_router(analytics.router, prefix=f"{settings.API_PREFIX}/analytics", tags=["analytics"])

@app.get("/")
def root():
    return {"message": "Welcome to the University Management System API"}
