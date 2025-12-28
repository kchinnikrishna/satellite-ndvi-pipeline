import time
import os
import sys

# Ensure python path sees root
sys.path.append("/app")

from shared.database import get_db
from shared.models import RawImageMetadata, NDVIRasterMetadata, NDVIStatistics
from ndvi_processing.processor import compute_ndvi, generate_preview, compute_statistics

def process_image(db, raw_image):
    print(f"Processing image ID {raw_image.id} ({raw_image.product_id})...")
    
    # Paths
    # Input path: replace /app/data with where we mapped it? 
    # Assumes docker volume setup matches paths or we use relative.
    # In ingestion we used /app/data/raw, let's assume shared volume at /app/data
    
    input_path = raw_image.file_path
    
    # Determine output paths
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = "/app/data/processed"
    os.makedirs(output_dir, exist_ok=True)
    
    ndvi_path = os.path.join(output_dir, f"{base_name}_ndvi.tiff")
    preview_path = os.path.join(output_dir, f"{base_name}_preview.png")
    
    try:
        # 1. Compute NDVI
        ndvi_data, profile = compute_ndvi(input_path, ndvi_path)
        
        # 2. Generate Preview
        generate_preview(ndvi_data, preview_path)
        
        # 3. Compute Stats
        stats = compute_statistics(ndvi_data)
        
        # 4. Save to DB
        
        # Create Raster Metadata
        raster_meta = NDVIRasterMetadata(
            raw_image_id=raw_image.id,
            file_path=ndvi_path,
            preview_path=preview_path,
            footprint=raw_image.footprint # Copy footprint
        )
        db.add(raster_meta)
        db.flush() # Get ID
        
        # Create Statistics Record
        # Histogram needs to be clean JSON
        stats_record = NDVIStatistics(
            ndvi_raster_id=raster_meta.id,
            mean_ndvi=stats["mean"],
            min_ndvi=stats["min"],
            max_ndvi=stats["max"],
            std_ndvi=stats["std"],
            class_histogram=stats["histogram"],
            geom=raw_image.footprint 
        )
        db.add(stats_record)
        
        # Update Raw Image Status
        raw_image.status = "PROCESSED"
        db.commit()
        print(f"Successfully processed {raw_image.product_id}")
        
    except Exception as e:
        print(f"Error processing {raw_image.product_id}: {e}")
        db.rollback()
        raw_image.status = "FAILED"
        db.commit() # Commit the failure status

def run_worker():
    print("Starting NDVI Processing Worker...")
    
    while True:
        db = next(get_db())
        try:
            # Find next downloaded image
            # Lock it? In simple case, just update status to PROCESSING immediately
            # Select first one
            raw_image = db.query(RawImageMetadata).filter(RawImageMetadata.status == "DOWNLOADED").first()
            
            if raw_image:
                raw_image.status = "PROCESSING"
                db.commit()
                # Process
                process_image(db, raw_image)
            else:
                # No work, sleep
                time.sleep(10)
                
        except Exception as e:
            print(f"Worker loop error: {e}")
            time.sleep(10)
        finally:
            db.close() # Ensure session is closed per loop iteration if manually managing

if __name__ == "__main__":
    run_worker()
