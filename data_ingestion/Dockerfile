FROM python:3.11-slim

# Install system dependencies (GDAL, PostGIS, etc.)
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set env vars for GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install Python deps
WORKDIR /app
COPY data_ingestion/requirements.txt . # If we had one, but we don't yet.
# Manual install for now or create requirements.txt
# Let's just install directly for simplicity in this generated file, 
# or better, create a requirements file in the previous steps? 
# I'll just install with pip here to be self-contained for the subagent, 
# but best practice is requirements.txt. 
# I will stick to inline installation for the "common" packages defined in user request.
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    rasterio \
    gdal==$(gdal-config --version) \
    numpy \
    psycopg2-binary \
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
