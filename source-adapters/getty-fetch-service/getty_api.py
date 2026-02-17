import os
from typing import List, Dict
import requests


class GettyClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.gettyimages.com/v3"

    def _headers(self) -> Dict[str, str]:
        return {
            "Api-Key": self.api_key,
            # Add auth headers / bearer token if required by Getty
        }

    def list_new_videos(self) -> List[dict]:
        # Placeholder: you’ll wire this to the real Getty endpoint/filters
        url = f"{self.base_url}/videos"
        params = {
            "page_size": 50,
            # e.g. "added_since": "2025-02-16T00:00:00Z"
        }
        resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        videos = []
        for item in data.get("videos", []):
            videos.append(
                {
                    "id": item["id"],
                    "video_url": item["display_sizes"][0]["uri"],
                }
            )
        return videos
