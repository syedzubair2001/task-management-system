from fastapi import FastAPI
from .database import engine, Base
from .routes import tasks
from fastapi.middleware.cors import CORSMiddleware

# Create DB tables
Base.metadata.create_all(bind=engine)

# FastAPI app instance
app = FastAPI(title="Task Management System")

# Allow frontend (React) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include task routes
app.include_router(tasks.router)

# Root endpoint
@app.get("/")
def root():
    return {"message": "Task Management API — visit /docs for OpenAPI UI"}
