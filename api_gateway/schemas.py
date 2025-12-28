from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class NDVIRasterResponse(BaseModel):
    id: int
    product_id: str
    acquisition_date: datetime
    ndvi_url: str = Field(description="URL to the NDVI GeoTIFF")
    preview_url: Optional[str] = Field(description="URL to the PNG preview")
    cloud_cover: Optional[float]

    class Config:
        from_attributes = True

class NDVIStatisticsResponse(BaseModel):
    id: int
    mean_ndvi: Optional[float]
    min_ndvi: Optional[float]
    max_ndvi: Optional[float]
    std_ndvi: Optional[float]
    class_histogram: Optional[Dict[str, int]]
    analysis_date: datetime

    class Config:
        from_attributes = True

class HealthCheck(BaseModel):
    status: str = "ok"
    db_connected: bool
