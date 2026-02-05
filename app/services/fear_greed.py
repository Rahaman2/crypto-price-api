import httpx
from datetime import datetime
from typing import Optional
from app.config import get_settings


class FearGreedService:
    def __init__(self):
        self.settings = get_settings()
        self.url = self.settings.fear_greed_url

    async def get_index(self) -> Optional[dict]:
        """Get the current Fear & Greed Index."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.url,
                params={"limit": 1},
                timeout=30.0,
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    item = data["data"][0]
                    return {
                        "value": int(item.get("value", 0)),
                        "classification": item.get("value_classification", "Unknown"),
                        "timestamp": datetime.fromtimestamp(int(item.get("timestamp", 0))),
                    }
            return None


fear_greed_service = FearGreedService()
