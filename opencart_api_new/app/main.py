import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router
from app.config import settings
from app.middleware.tracking import TrackingMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add tracking middleware
app.add_middleware(TrackingMiddleware)

# Include API routes
app.include_router(router, prefix="/api")

@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API version {settings.PROJECT_VERSION}",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)