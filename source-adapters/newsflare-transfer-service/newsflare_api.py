from typing import List, Dict
import requests


class NewsflareClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.newsflare.com/v1"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
        }

    def list_new_videos(self) -> List[dict]:
        # Placeholder: wire to real Newsflare endpoint/filters
        url = f"{self.base_url}/videos"
        params = {
            "limit": 50,
            # e.g. "since": "2025-02-16T00:00:00Z"
        }
        resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        videos = []
        for item in data.get("data", []):
            videos.append(
                {
                    "id": item["id"],
                    "video_url": item["file_url"],  # adjust to real field
                }
            )
        return videos
