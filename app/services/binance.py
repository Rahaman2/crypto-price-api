import httpx
from typing import Optional
from datetime import datetime, timezone


class BinanceService:
    def __init__(self):
        self.base_url = "https://api.binance.com"

    def _format_symbol(self, symbol: str) -> str:
        """Convert symbol to Binance format (e.g., btc -> BTCUSDT)."""
        symbol = symbol.upper().strip()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        return symbol

    async def get_price(self, symbol: str) -> Optional[dict]:
        """
        Get current price and 24h stats for a trading pair.

        Args:
            symbol: Coin symbol (e.g., "BTC", "ETH", "SOL")

        Returns:
            Price data dict or None if not found
        """
        binance_symbol = self._format_symbol(symbol)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v3/ticker/24hr",
                params={"symbol": binance_symbol},
                timeout=10.0,
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "symbol": symbol.upper(),
                    "name": None,  # Binance doesn't provide coin name
                    "price_usd": float(data.get("lastPrice", 0)),
                    "price_change_24h": float(data.get("priceChangePercent", 0)),
                    "market_cap": None,  # Binance doesn't provide market cap
                    "volume_24h": float(data.get("quoteVolume", 0)),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "source": "binance",
                }
            return None

    async def get_all_prices(self) -> list[dict]:
        """Get prices for all USDT trading pairs."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v3/ticker/price",
                timeout=10.0,
            )

            if response.status_code == 200:
                data = response.json()
                # Filter for USDT pairs only
                return [
                    {
                        "symbol": item["symbol"].replace("USDT", ""),
                        "price_usd": float(item["price"]),
                    }
                    for item in data
                    if item["symbol"].endswith("USDT")
                ]
            return []


binance_service = BinanceService()
