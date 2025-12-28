from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

# Internal imports
from shared.database import get_db
from shared.models import RawImageMetadata, NDVIRasterMetadata, NDVIStatistics
from api_gateway.schemas import NDVIRasterResponse, NDVIStatisticsResponse

import json
from geoalchemy2 import WKTElement
from geoalchemy2.shape import from_shape
from shapely.geometry import shape, box

router = APIRouter(
    prefix="/ndvi",
    tags=["ndvi"]
)

@router.get("/tiles", response_model=List[NDVIRasterResponse])
def get_ndvi_tiles(
    bbox: str = Query(..., description="BBox as 'minx,miny,maxx,maxy'"),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    db: Session = Depends(get_db)
):
    try:
        parts = [float(x) for x in bbox.split(',')]
        if len(parts) != 4:
            raise ValueError
        minx, miny, maxx, maxy = parts
        query_geom = WKTElement(f"POLYGON(({minx} {miny}, {maxx} {miny}, {maxx} {maxy}, {minx} {maxy}, {minx} {miny}))", srid=4326)
    except Exception:
         raise HTTPException(status_code=400, detail="Invalid bbox format. Expected 'minx,miny,maxx,maxy'")

    query = db.query(NDVIRasterMetadata).join(NDVIRasterMetadata.raw_image)
    
    # Filter by geometry
    query = query.filter(func.ST_Intersects(NDVIRasterMetadata.footprint, query_geom))

    # Filter by date
    if start_date:
        query = query.filter(RawImageMetadata.acquisition_date >= start_date)
    if end_date:
        query = query.filter(RawImageMetadata.acquisition_date <= end_date)

    results = query.all()
    
    # Map to schema
    response = []
    for r in results:
        response.append(NDVIRasterResponse(
            id=r.id,
            product_id=r.raw_image.product_id,
            acquisition_date=r.raw_image.acquisition_date,
            ndvi_url=f"/static/{r.file_path.split('/')[-1]}", # Simple mapping for now
            preview_url=f"/static/{r.preview_path.split('/')[-1]}" if r.preview_path else None,
            cloud_cover=r.raw_image.cloud_cover
        ))
        
    return response

@router.get("/statistics", response_model=List[NDVIStatisticsResponse])
def get_statistics(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    db: Session = Depends(get_db)
):
    # Retrieve all pre-calculated stats inside the time range
    # In a real app we might spatial filter these too
    query = db.query(NDVIStatistics)
    
    if start_date:
        query = query.filter(NDVIStatistics.analysis_date >= start_date)
    if end_date:
        query = query.filter(NDVIStatistics.analysis_date <= end_date)
        
    return query.limit(50).all()
