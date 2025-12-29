FROM python:3.11-slim

# Install system dependencies
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
RUN pip install --no-cache-dir \
    rasterio \
    gdal==$(gdal-config --version) \
    numpy \
    psycopg2-binary \
    shapely \
    sqlalchemy \
    geoalchemy2 \
    matplotlib \
    requests \
    pydantic

WORKDIR /app

# Copy code
COPY shared /app/shared
COPY ndvi_processing /app/ndvi_processing

# Set Python path
ENV PYTHONPATH=/app

# Make sure data dirs exist (though volume mount keeps them)
RUN mkdir -p /app/data/processed

# Entrypoint
CMD ["python", "ndvi_processing/worker.py"]
