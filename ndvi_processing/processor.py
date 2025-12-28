import numpy as np
import rasterio
import matplotlib.pyplot as plt
import os
import json
from rasterio.transform import from_origin
from rasterio.enums import Resampling

def compute_ndvi(input_path, output_path):
    """
    Computes NDVI from a multi-band GeoTIFF containing B04 (Red) and B08 (NIR).
    Assumes band 1 is Red and band 2 is NIR.
    """
    with rasterio.open(input_path) as src:
        red = src.read(1).astype('float32')
        nir = src.read(2).astype('float32')
        profile = src.profile
        
        # Avoid division by zero
        # NDVI = (NIR - Red) / (NIR + Red)
        numerator = nir - red
        denominator = nir + red
        
        # Prepare NDVI array, initialized with NaNs
        ndvi = np.full(red.shape, np.nan, dtype='float32')
        
        # Safe division
        np.seterr(divide='ignore', invalid='ignore')
        mask = (denominator != 0)
        ndvi[mask] = numerator[mask] / denominator[mask]
        
        # Clip to valid range just in case
        ndvi = np.clip(ndvi, -1.0, 1.0)
        
        # Update profile for single band float output
        profile.update(
            dtype=rasterio.float32,
            count=1,
            driver='GTiff',
            compress='lzw'
        )
        
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(ndvi, 1)
            
    return ndvi, profile

def generate_preview(ndvi_array, output_png_path):
    """
    Generates a colorized PNG preview of the NDVI array.
    """
    plt.figure(figsize=(10, 10))
    # Use a diverging colormap or specific one for vegetation
    cmap = plt.cm.RdYlGn 
    plt.imshow(ndvi_array, cmap=cmap, vmin=-1.0, vmax=1.0)
    plt.axis('off')
    plt.savefig(output_png_path, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()

def compute_statistics(ndvi_array):
    """
    Computes vector statistics and histogram from the NDVI array.
    """
    # Filter out NaNs for stats
    valid_pixels = ndvi_array[~np.isnan(ndvi_array)]
    
    if valid_pixels.size == 0:
        return {
            "mean": None, "min": None, "max": None, "std": None, "histogram": {}
        }
        
    stats = {
        "mean": float(np.mean(valid_pixels)),
        "min": float(np.min(valid_pixels)),
        "max": float(np.max(valid_pixels)),
        "std": float(np.std(valid_pixels))
    }
    
    # Classification histogram
    # classifications = [
    #   { "label": "water_or_cloud", "min": -1.0, "max": 0.0 },
    #   { "label": "bare_soil_or_builtup", "min": 0.0, "max": 0.2 },
    #   { "label": "stressed_vegetation", "min": 0.2, "max": 0.4 },
    #   { "label": "moderate_vegetation", "min": 0.4, "max": 0.6 },
    #   { "label": "dense_vegetation", "min": 0.6, "max": 1.0 }
    # ]
    
    histogram = {
        "water_or_cloud": int(np.sum((valid_pixels >= -1.0) & (valid_pixels < 0.0))),
        "bare_soil_or_builtup": int(np.sum((valid_pixels >= 0.0) & (valid_pixels < 0.2))),
        "stressed_vegetation": int(np.sum((valid_pixels >= 0.2) & (valid_pixels < 0.4))),
        "moderate_vegetation": int(np.sum((valid_pixels >= 0.4) & (valid_pixels < 0.6))),
        "dense_vegetation": int(np.sum((valid_pixels >= 0.6) & (valid_pixels <= 1.0)))
    }
    
    stats["histogram"] = histogram
    return stats
