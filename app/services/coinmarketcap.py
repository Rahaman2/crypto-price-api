from cryptocmd import CmcScraper
from datetime import datetime, timedelta
from typing import Optional


class CoinMarketCapService:
    def get_historical_data(
        self,
        coin_code: str,
        days: int = 30,
        coin_name: Optional[str] = None,
    ) -> list[dict]:
        """
        Get historical OHLC data for a coin using cryptoCMD.

        Args:
            coin_code: The coin symbol (e.g., "BTC", "ETH")
            days: Number of days of history to fetch
            coin_name: Optional coin name for disambiguation

        Returns:
            List of historical data points with OHLC values
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        start_str = start_date.strftime("%d-%m-%Y")
        end_str = end_date.strftime("%d-%m-%Y")

        try:
            if coin_name:
                scraper = CmcScraper(
                    coin_code=coin_code.lower(),
                    coin_name=coin_name.lower(),
                    start_date=start_str,
                    end_date=end_str,
                )
            else:
                scraper = CmcScraper(
                    coin_code=coin_code.lower(),
                    start_date=start_str,
                    end_date=end_str,
                )

            df = scraper.get_dataframe()

            if df is None or df.empty:
                return []

            result = []
            for _, row in df.iterrows():
                result.append({
                    "date": row["Date"].strftime("%Y-%m-%d") if hasattr(row["Date"], "strftime") else str(row["Date"]),
                    "open": float(row["Open"]) if row["Open"] else 0.0,
                    "high": float(row["High"]) if row["High"] else 0.0,
                    "low": float(row["Low"]) if row["Low"] else 0.0,
                    "close": float(row["Close"]) if row["Close"] else 0.0,
                    "volume": float(row["Volume"]) if row.get("Volume") else None,
                    "market_cap": float(row["Market Cap"]) if row.get("Market Cap") else None,
                })

            return result

        except Exception as e:
            # Log error in production
            print(f"Error fetching historical data: {e}")
            return []


coinmarketcap_service = CoinMarketCapService()
