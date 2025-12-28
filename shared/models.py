from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from sqlalchemy.sql import func
from .database import Base

class RawImageMetadata(Base):
    __tablename__ = "raw_image_metadata"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, unique=True, nullable=False)
    acquisition_date = Column(DateTime(timezone=True), nullable=False)
    cloud_cover = Column(Float)
    platform = Column(String)
    status = Column(String, default="DOWNLOADED")
    file_path = Column(String)
    footprint = Column(Geometry("POLYGON", srid=4326))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ndvi_rasters = relationship("NDVIRasterMetadata", back_populates="raw_image")

class NDVIRasterMetadata(Base):
    __tablename__ = "ndvi_raster_metadata"

    id = Column(Integer, primary_key=True, index=True)
    raw_image_id = Column(Integer, ForeignKey("raw_image_metadata.id"))
    file_path = Column(String, nullable=False)
    preview_path = Column(String)
    generation_date = Column(DateTime(timezone=True), server_default=func.now())
    footprint = Column(Geometry("POLYGON", srid=4326))

    # Relationships
    raw_image = relationship("RawImageMetadata", back_populates="ndvi_rasters")
    statistics = relationship("NDVIStatistics", back_populates="ndvi_raster")

class NDVIStatistics(Base):
    __tablename__ = "ndvi_statistics"

    id = Column(Integer, primary_key=True, index=True)
    ndvi_raster_id = Column(Integer, ForeignKey("ndvi_raster_metadata.id"))
    mean_ndvi = Column(Float)
    min_ndvi = Column(Float)
    max_ndvi = Column(Float)
    std_ndvi = Column(Float)
    class_histogram = Column(JSONB)
    geom = Column(Geometry("POLYGON", srid=4326))
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ndvi_raster = relationship("NDVIRasterMetadata", back_populates="statistics")
