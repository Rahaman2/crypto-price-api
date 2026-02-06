from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import httpx

router = APIRouter()


@router.get("/list")
async def get_exchanges(
    limit: int = Query(default=20, ge=1, le=100, description="Number of exchanges"),
):
    """
    Get list of cryptocurrency exchanges ranked by trust score and volume.

    - **limit**: Number of exchanges to return (1-100)
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://api.coingecko.com/api/v3/exchanges",
                params={"per_page": limit}
            )

            if response.status_code == 200:
                exchanges = response.json()
                return {
                    "count": len(exchanges),
                    "exchanges": [
                        {
                            "id": ex.get("id"),
                            "name": ex.get("name"),
                            "country": ex.get("country"),
                            "trust_score": ex.get("trust_score"),
                            "trust_rank": ex.get("trust_score_rank"),
                            "volume_24h_btc": ex.get("trade_volume_24h_btc"),
                            "year_established": ex.get("year_established"),
                            "url": ex.get("url"),
                            "image": ex.get("image"),
                        }
                        for ex in exchanges
                    ]
                }
    except Exception as e:
        raise HTTPException(status_code=503, detail="Unable to fetch exchanges")

    raise HTTPException(status_code=503, detail="Exchange data unavailable")


@router.get("/{exchange_id}")
async def get_exchange_details(exchange_id: str):
    """
    Get detailed information about a specific exchange.

    - **exchange_id**: Exchange ID (e.g., "binance", "coinbase")
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"https://api.coingecko.com/api/v3/exchanges/{exchange_id}"
            )

            if response.status_code == 200:
                ex = response.json()
                return {
                    "id": ex.get("id"),
                    "name": ex.get("name"),
                    "country": ex.get("country"),
                    "description": ex.get("description"),
                    "trust_score": ex.get("trust_score"),
                    "trust_rank": ex.get("trust_score_rank"),
                    "volume_24h_btc": ex.get("trade_volume_24h_btc"),
                    "year_established": ex.get("year_established"),
                    "url": ex.get("url"),
                    "image": ex.get("image"),
                    "facebook_url": ex.get("facebook_url"),
                    "twitter_handle": ex.get("twitter_handle"),
                    "telegram_url": ex.get("telegram_url"),
                    "slack_url": ex.get("slack_url"),
                    "has_trading_incentive": ex.get("has_trading_incentive"),
                    "tickers_count": len(ex.get("tickers", [])),
                }
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Exchange '{exchange_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail="Unable to fetch exchange details")


@router.get("/{exchange_id}/tickers")
async def get_exchange_tickers(
    exchange_id: str,
    limit: int = Query(default=50, ge=1, le=100, description="Number of trading pairs"),
):
    """
    Get trading pairs (tickers) for a specific exchange.

    - **exchange_id**: Exchange ID (e.g., "binance")
    - **limit**: Number of trading pairs to return
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"https://api.coingecko.com/api/v3/exchanges/{exchange_id}/tickers",
                params={"page": 1}
            )

            if response.status_code == 200:
                data = response.json()
                tickers = data.get("tickers", [])[:limit]
                return {
                    "exchange": exchange_id,
                    "count": len(tickers),
                    "tickers": [
                        {
                            "base": t.get("base"),
                            "target": t.get("target"),
                            "last_price": t.get("last"),
                            "volume": t.get("volume"),
                            "spread": t.get("bid_ask_spread_percentage"),
                            "trade_url": t.get("trade_url"),
                            "trust_score": t.get("trust_score"),
                        }
                        for t in tickers
                    ]
                }
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Exchange '{exchange_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail="Unable to fetch tickers")
