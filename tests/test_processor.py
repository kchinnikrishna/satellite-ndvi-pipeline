import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import numpy as np

# MOCK MODULES BEFORE IMPORT
sys.modules['rasterio'] = MagicMock()
sys.modules['rasterio.transform'] = MagicMock()
sys.modules['rasterio.enums'] = MagicMock()
sys.modules['matplotlib'] = MagicMock()
sys.modules['matplotlib.pyplot'] = MagicMock()

# Now import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ndvi_processing.processor import compute_ndvi, compute_statistics

class TestNDVIProcessor(unittest.TestCase):
    
    @patch('ndvi_processing.processor.rasterio')
    def test_compute_ndvi_logic(self, mock_rasterio):
        # Setup mock
        mock_src = MagicMock()
        mock_rasterio.open.return_value.__enter__.return_value = mock_src
        
        red_band = np.array([[100, 100], [200, 0]], dtype='float32')
        nir_band = np.array([[500, 100], [100, 0]], dtype='float32')
        
        def side_effect(band_idx):
            if band_idx == 1: return red_band
            if band_idx == 2: return nir_band
            return None
            
        mock_src.read.side_effect = side_effect
        mock_src.profile = {'driver': 'GTiff'}
        
        # Run
        ndvi, profile = compute_ndvi("dummy_input.tiff", "dummy_output.tiff")
        
        # Verify values
        self.assertAlmostEqual(ndvi[0, 0], 2/3, places=4)
        self.assertAlmostEqual(ndvi[0, 1], 0.0, places=2)
        self.assertAlmostEqual(ndvi[1, 0], -0.33, places=2)
        self.assertTrue(np.isnan(ndvi[1, 1]))

    def test_compute_statistics(self):
        ndvi = np.array([0.7, 0.5, 0.3, 0.1, -0.2, np.nan])
        stats = compute_statistics(ndvi)
        
        self.assertAlmostEqual(stats['mean'], 0.28, places=2)
        self.assertEqual(stats['max'], 0.7)
        self.assertEqual(stats['min'], -0.2)
        
        hist = stats['histogram']
        self.assertEqual(hist['water_or_cloud'], 1)
        self.assertEqual(hist['bare_soil_or_builtup'], 1)
        self.assertEqual(hist['stressed_vegetation'], 1)
        self.assertEqual(hist['moderate_vegetation'], 1)
        self.assertEqual(hist['dense_vegetation'], 1)

if __name__ == '__main__':
    unittest.main()
