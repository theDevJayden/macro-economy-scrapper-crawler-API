from fastapi import FastAPI
from app.api.macro import router as macro_router

# Initialize FastAPI Application
app = FastAPI(
    title="Global Macro & Stock Intelligence API",
    description="Backend Crawler, Scraper, and Data Engine for A2A AI Agents.",
    version="1.0.0"
)

# Root/Healthcheck Endpoint
@app.get("/")
def root():
    return {
        "service": "Global Macro Intelligence Engine",
        "status": "online",
        "docs_url": "http://localhost:8000/docs"
    }

# Register the Macro Router from app/api/macro.py
app.include_router(macro_router)