from fastapi import FastAPI
from app.routers import analytics, webhooks

app = FastAPI(title="Travelink Analytics & Webhooks")

app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

@app.get("/")
def root():
    return {"service": "Python FastAPI - Analytics & Notify"}
