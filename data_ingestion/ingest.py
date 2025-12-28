import os
import json
import time
import argparse
from datetime import datetime, timedelta
from typing import List

# Internal imports
# Assuming the package structure allows this, or we adjust sys.path in Docker
from shared.database import get_db
from shared.models import RawImageMetadata
from data_ingestion.sentinel_client import SentinelClient
from sqlalchemy.orm import Session

def get_aoi():
    """
    Retrieves AOI from env or arguments.
    Defaults to a small box if not set.
    """
    aoi_str = os.getenv("DEFAULT_AOI_GEOJSON")
    if aoi_str:
        return json.loads(aoi_str)
    
    # Default: Small area in San Francisco
    return {
        "type": "Polygon",
        "coordinates": [[
            [-122.51, 37.71],
            [-122.35, 37.71],
            [-122.35, 37.81],
            [-122.51, 37.81],
            [-122.51, 37.71]
        ]]
    }

def get_time_range():
    """
    Parses start/end date from env or uses default last 30 days.
    """
    time_range_str = os.getenv("DEFAULT_TIME_RANGE")
    if time_range_str:
        start, end = time_range_str.split('/')
        return start, end
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def image_exists(db: Session, product_id: str) -> bool:
    return db.query(RawImageMetadata).filter(RawImageMetadata.product_id == product_id).first() is not None

def run_ingestion():
    print("Starting ingestion job...")
    
    db = next(get_db())
    client = SentinelClient()
    aoi = get_aoi()
    start_date, end_date = get_time_range()
    
    print(f"Searching for scenes in range {start_date} to {end_date}...")
    
    # Search
    scenes = client.search_scenes(aoi, (start_date, end_date))
    print(f"Found {len(scenes)} potential scenes.")
    
    download_dir = "/app/data/raw"
    os.makedirs(download_dir, exist_ok=True)
    
    for scene in scenes:
        props = scene.get("properties", {})
        product_id = scene.get("id")
        acquisition_date = props.get("datetime")
        cloud_cover = props.get("eo:cloud_cover", 0.0)
        
        # Check cloud cover threshold
        max_cloud = float(os.getenv("MAX_CLOUD_COVER", 100))
        if cloud_cover > max_cloud:
            print(f"Skipping {product_id} due to cloud cover {cloud_cover}% > {max_cloud}%")
            continue
            
        if image_exists(db, product_id):
            print(f"Scene {product_id} already exists in DB. Skipping.")
            continue
            
        print(f"Downloading {product_id}...")
        
        # Construct BBOX from AOI for simplicity in this demo
        # In prod, we'd use the scene geometry or precise AOI clipping
        coords = aoi["coordinates"][0]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        bbox = [min(lons), min(lats), max(lons), max(lats)]
        
        filename = f"{product_id}.tiff"
        file_path = os.path.join(download_dir, filename)
        
        try:
            # client.download_image(bbox, (start_date, end_date), file_path)
            # In a real run, we verify date match. 
            # For simplicity using the scene timestamp for the single request
            scene_time = acquisition_date
            # Broaden slightly for the API request
            client.download_image(bbox, (start_date, end_date), file_path)
            
            # Insert into DB
            # Note: Footprint needs to be WKT or WKB for GeoAlchemy usually, 
            # or use ST_GeomFromGeoJSON if we pass dict. 
            # Here we just use a placeholder WKT for simplicity or convert.
            
            # Simple WKT conversion for the box
            wkt_poly = f"POLYGON(({bbox[0]} {bbox[1]}, {bbox[2]} {bbox[1]}, {bbox[2]} {bbox[3]}, {bbox[0]} {bbox[3]}, {bbox[0]} {bbox[1]}))"
            
            record = RawImageMetadata(
                product_id=product_id,
                acquisition_date=acquisition_date,
                cloud_cover=cloud_cover,
                platform="Sentinel-2",
                status="DOWNLOADED",
                file_path=file_path,
                footprint=wkt_poly
            )
            db.add(record)
            db.commit()
            print(f"Successfully ingested {product_id}")
            
        except Exception as e:
            print(f"Failed to ingest {product_id}: {e}")
            db.rollback()

if __name__ == "__main__":
    run_ingestion()
