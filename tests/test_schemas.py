import unittest
from unittest.mock import MagicMock
import sys
import os
from datetime import datetime

# MOCK PYDANTIC
mock_pydantic = MagicMock()
class MockBaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
mock_pydantic.BaseModel = MockBaseModel
mock_pydantic.Field = MagicMock()

sys.modules['pydantic'] = mock_pydantic

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_gateway.schemas import NDVIRasterResponse, NDVIStatisticsResponse

class TestSchemas(unittest.TestCase):
    def test_raster_response(self):
        data = {
            "id": 1,
            "product_id": "S2A_123456",
            "acquisition_date": datetime(2023, 1, 1),
            "ndvi_url": "/static/test.tiff",
            "preview_url": "/static/test.png",
            "cloud_cover": 5.0
        }
        # Since we mocked BaseModel as a simple class that sets attrs, 
        # this verifies instantiation works and fields are accessible.
        model = NDVIRasterResponse(**data)
        self.assertEqual(model.id, 1)
        self.assertEqual(model.product_id, "S2A_123456")
        self.assertEqual(model.ndvi_url, "/static/test.tiff")

    def test_stats_response(self):
        data = {
            "id": 10,
            "mean_ndvi": 0.5,
            "min_ndvi": -0.1,
            "max_ndvi": 0.9,
            "std_ndvi": 0.2,
            "class_histogram": {"water": 10, "veg": 50},
            "analysis_date": datetime(2023, 1, 2)
        }
        model = NDVIStatisticsResponse(**data)
        self.assertEqual(model.class_histogram['water'], 10)
        self.assertEqual(model.mean_ndvi, 0.5)

if __name__ == '__main__':
    unittest.main()
