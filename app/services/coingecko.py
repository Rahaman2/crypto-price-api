import httpx
from typing import Optional
from app.config import get_settings


class CoinGeckoService:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.coingecko_base_url

    async def get_price(self, coin_id: str) -> Optional[dict]:
        """Get current price for a coin by its CoinGecko ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/coins/{coin_id}",
                params={
                    "localization": "false",
                    "tickers": "false",
                    "community_data": "false",
                    "developer_data": "false",
                },
                timeout=30.0,
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "symbol": data.get("symbol", "").upper(),
                    "name": data.get("name"),
                    "price_usd": data.get("market_data", {}).get("current_price", {}).get("usd"),
                    "price_change_24h": data.get("market_data", {}).get("price_change_percentage_24h"),
                    "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd"),
                    "volume_24h": data.get("market_data", {}).get("total_volume", {}).get("usd"),
                    "last_updated": data.get("last_updated"),
                }
            return None

    async def get_top_coins(self, limit: int = 100) -> list[dict]:
        """Get top coins by market cap."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": limit,
                    "page": 1,
                    "sparkline": "false",
                },
                timeout=30.0,
            )
            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        "rank": coin.get("market_cap_rank"),
                        "symbol": coin.get("symbol", "").upper(),
                        "name": coin.get("name"),
                        "price_usd": coin.get("current_price"),
                        "market_cap": coin.get("market_cap"),
                        "price_change_24h": coin.get("price_change_percentage_24h"),
                    }
                    for coin in data
                ]
            return []

    async def get_trending(self) -> list[dict]:
        """Get trending coins."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search/trending",
                timeout=30.0,
            )
            if response.status_code == 200:
                data = response.json()
                coins = data.get("coins", [])
                return [
                    {
                        "symbol": coin.get("item", {}).get("symbol", "").upper(),
                        "name": coin.get("item", {}).get("name"),
                        "market_cap_rank": coin.get("item", {}).get("market_cap_rank"),
                        "price_btc": coin.get("item", {}).get("price_btc"),
                    }
                    for coin in coins
                ]
            return []

    async def search_coin(self, query: str) -> Optional[str]:
        """Search for a coin and return its CoinGecko ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search",
                params={"query": query},
                timeout=30.0,
            )
            if response.status_code == 200:
                data = response.json()
                coins = data.get("coins", [])
                if coins:
                    # Return the first match's ID
                    return coins[0].get("id")
            return None

    def _get_valid_ohlc_days(self, days: int) -> int:
        """Map requested days to valid CoinGecko OHLC API values."""
        valid_days = [1, 7, 14, 30, 90, 180, 365]
        for valid in valid_days:
            if days <= valid:
                return valid
        return 365

    async def get_historical_data(self, coin_id: str, days: int = 30) -> list[dict]:
        """Get historical OHLC data for a coin."""
        # CoinGecko OHLC API only accepts specific day values
        api_days = self._get_valid_ohlc_days(days)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/coins/{coin_id}/ohlc",
                params={
                    "vs_currency": "usd",
                    "days": api_days,
                },
                timeout=30.0,
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "error" in data:
                    return []

                from datetime import datetime
                result = []
                seen_dates = set()

                for item in data:
                    # item format: [timestamp, open, high, low, close]
                    timestamp = item[0] / 1000  # Convert ms to seconds
                    date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

                    # Only keep one entry per day (latest)
                    if date_str not in seen_dates:
                        seen_dates.add(date_str)
                        result.append({
                            "date": date_str,
                            "open": float(item[1]) if item[1] else 0.0,
                            "high": float(item[2]) if item[2] else 0.0,
                            "low": float(item[3]) if item[3] else 0.0,
                            "close": float(item[4]) if item[4] else 0.0,
                            "volume": None,
                            "market_cap": None,
                        })

                # Return only the requested number of days (most recent)
                return result[-days:] if len(result) > days else result
            return []


coingecko_service = CoinGeckoService()
