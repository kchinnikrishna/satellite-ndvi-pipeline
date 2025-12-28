FROM python:3.11-slim

# Install system dependencies
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
    prometheus-fastapi-instrumentator \
    pydantic

WORKDIR /app

# Copy code
COPY shared /app/shared
# Copy api_gateway (using correct context from compose)
COPY api_gateway /app/api_gateway

# Set Python path
ENV PYTHONPATH=/app

# Entrypoint
CMD ["uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
