from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import Database Session and Base
from app.db.session import engine, Base

# Import Routers
from app.api.endpoints.user import router as users_router
from app.api.endpoints.school import router as schools_router
from app.api.endpoints.student import router as students_router
from app.api.endpoints.class_api import router as classes_router
from app.api.endpoints.attendance import router as attendance_router

# Create tables in the database (SQLAlchemy will skip existing tables)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="School Management API",
    description="Professional API for School Management System",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(schools_router)
app.include_router(users_router)
app.include_router(students_router)
app.include_router(classes_router)
app.include_router(attendance_router)

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API status.
    """
    return {"status": "ok", "message": "School Management API is running"}