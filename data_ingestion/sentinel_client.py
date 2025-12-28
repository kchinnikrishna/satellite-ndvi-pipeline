import os
import requests
import time
from datetime import datetime

class SentinelClient:
    def __init__(self):
        self.client_id = os.getenv("SENTINEL_HUB_CLIENT_ID")
        self.client_secret = os.getenv("SENTINEL_HUB_CLIENT_SECRET")
        self.instance_id = os.getenv("SENTINEL_HUB_INSTANCE_ID")
        self.token = None
        self.token_expiry = 0
        
        # Base URLs
        self.auth_url = "https://services.sentinel-hub.com/oauth/token"
        self.process_url = "https://services.sentinel-hub.com/api/v1/process"
        self.catalog_url = "https://services.sentinel-hub.com/api/v1/catalog/1.0.0/search"

    def _get_token(self):
        """
        Obtains or refreshes the OAuth2 token.
        """
        if self.token and time.time() < self.token_expiry:
            return self.token
            
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(self.auth_url, data=payload)
            response.raise_for_status()
            data = response.json()
            self.token = data["access_token"]
            # Set expiry with a small buffer
            self.token_expiry = time.time() + data["expires_in"] - 60
            return self.token
        except Exception as e:
            print(f"Error authenticating with Sentinel Hub: {e}")
            raise

    def search_scenes(self, aoi_geometry, time_range):
        """
        Search for available Sentinel-2 scenes in the given AOI and time range.
        aoi_geometry: GeoJSON-like dict (WGS84)
        time_range: tuple (start_date_iso, end_date_iso)
        """
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        start_date, end_date = time_range
        
        payload = {
            "collections": ["sentinel-2-l2a"],
            "datetime": f"{start_date}/{end_date}",
            "intersects": aoi_geometry,
            "limit": 10
        }
        
        try:
            response = requests.post(self.catalog_url, json=payload, headers=headers)
            response.raise_for_status()
            features = response.json().get("features", [])
            # Filter for cloud cover if needed, though usually done in payload
            # Returning minimal info
            return features
        except Exception as e:
            print(f"Error searches scenes: {e}")
            return []

    def download_image(self, bbox, time_interval, output_path):
        """
        Downloads B04 (Red) and B08 (NIR) bands as a multi-band GeoTIFF.
        bbox: list [minx, miny, maxx, maxy]
        """
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/x-tar"
        }
        
        evalscript = """
        //VERSION=3
        function setup() {
          return {
            input: ["B04", "B08"],
            output: { bands: 2, sampleType: "UINT16" }
          };
        }

        function evaluatePixel(sample) {
          return [sample.B04, sample.B08];
        }
        """

        payload = {
            "input": {
                "bounds": {
                    "bbox": bbox,
                    "properties": { "crs": "http://www.opengis.net/def/crs/EPSG/0/4326" }
                },
                "data": [{
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": time_interval[0],
                            "to": time_interval[1]
                        }
                    }
                }]
            },
            "output": {
                "width": 512,
                "height": 512,
                "responses": [
                    {
                        "identifier": "default",
                        "format": { "type": "image/tiff" }
                    }
                ]
            },
            "evalscript": evalscript
        }
        
        try:
            response = requests.post(self.process_url, json=payload, headers=headers)
            response.raise_for_status()
            
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            return output_path
        except Exception as e:
            print(f"Error downloading image: {e}")
            raise
