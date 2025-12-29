FROM python:3.11-slim

# Install system dependencies (GDAL, PostGIS, etc.)
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    libpq-dev \
    libpq-dev \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set env vars for GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install Python deps
WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    rasterio \
    gdal==$(gdal-config --version) \
    numpy \
    psycopg2-binary \
    shapely \
    sqlalchemy \
    geoalchemy2 \
    requests \
    pydantic

# Copy code
COPY shared /app/shared
COPY data_ingestion /app/data_ingestion

# Set Python path
ENV PYTHONPATH=/app

# Entrypoint
CMD ["python", "data_ingestion/ingest.py"]
