-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Table to store metadata about downloaded raw images
CREATE TABLE IF NOT EXISTS raw_image_metadata (
    id SERIAL PRIMARY KEY,
    product_id TEXT NOT NULL UNIQUE, -- Sentinel-2 product ID
    acquisition_date TIMESTAMP WITH TIME ZONE NOT NULL,
    cloud_cover FLOAT,
    platform TEXT, -- e.g., 'Sentinel-2'
    status TEXT DEFAULT 'DOWNLOADED', -- 'DOWNLOADED', 'PROCESSING', 'PROCESSED', 'FAILED'
    file_path TEXT, -- Path to local directory where GeoTIFFs are stored
    footprint GEOMETRY(Polygon, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index on footprint for spatial queries
CREATE INDEX IF NOT EXISTS raw_image_footprint_idx ON raw_image_metadata USING GIST(footprint);


-- Table to store metadata about computed NDVI rasters
CREATE TABLE IF NOT EXISTS ndvi_raster_metadata (
    id SERIAL PRIMARY KEY,
    raw_image_id INTEGER REFERENCES raw_image_metadata(id),
    file_path TEXT NOT NULL, -- Path to NDVI GeoTIFF
    preview_path TEXT, -- Path to PNG preview
    generation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    footprint GEOMETRY(Polygon, 4326)
);

CREATE INDEX IF NOT EXISTS ndvi_raster_footprint_idx ON ndvi_raster_metadata USING GIST(footprint);


-- Table to store computed statistics (vector results)
CREATE TABLE IF NOT EXISTS ndvi_statistics (
    id SERIAL PRIMARY KEY,
    ndvi_raster_id INTEGER REFERENCES ndvi_raster_metadata(id),
    mean_ndvi FLOAT,
    min_ndvi FLOAT,
    max_ndvi FLOAT,
    std_ndvi FLOAT,
    -- Histogram as JSONB: {"water": 10, "vegetation": 500, ...} or buckets
    class_histogram JSONB, 
    geom GEOMETRY(Polygon, 4326), -- The AOI used for stats
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ndvi_stats_geom_idx ON ndvi_statistics USING GIST(geom);
