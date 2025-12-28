from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from api_gateway.routers import ndvi
import os

app = FastAPI(
    title="Satellite NDVI Pipeline API",
    description="API for querying Sentinel-2 NDVI results",
    version="0.1.0"
)

# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (for images)
# In production, use nginx or S3 presigned URLs
os.makedirs("/app/data/processed", exist_ok=True)
app.mount("/static", StaticFiles(directory="/app/data/processed"), name="static")

# Instrument Prometheus
Instrumentator().instrument(app).expose(app)

# Routers
app.include_router(ndvi.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "api_gateway"}
