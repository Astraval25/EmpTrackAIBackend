from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.api.v1.routes.user_route import router as user_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EmpTrackAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "healthy"}