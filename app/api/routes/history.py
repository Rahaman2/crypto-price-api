from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.schemas import HistoryResponse, HistoricalDataPoint
from app.services.coingecko import coingecko_service
from app.services.coinmarketcap import coinmarketcap_service

router = APIRouter()


@router.get("/{symbol}", response_model=HistoryResponse)
async def get_history(
    symbol: str,
    days: int = Query(default=30, ge=1, le=365, description="Number of days of history"),
    coin_name: Optional[str] = Query(default=None, description="Coin name for disambiguation"),
):
    """
    Get historical OHLC data for a cryptocurrency.

    - **symbol**: Coin symbol or ID (e.g., "bitcoin", "ethereum", "btc")
    - **days**: Number of days of history (1-365, default: 30)
    - **coin_name**: Optional coin name for disambiguation (e.g., "solana" for SOL)
    """
    # Try CoinGecko first (more reliable API)
    coin_id = symbol.lower()

    # If symbol is short (like BTC), search for the full ID
    if len(symbol) <= 5:
        found_id = await coingecko_service.search_coin(symbol)
        if found_id:
            coin_id = found_id

    data = await coingecko_service.get_historical_data(coin_id=coin_id, days=days)

    # Fallback to cryptoCMD if CoinGecko fails
    if not data:
        data = coinmarketcap_service.get_historical_data(
            coin_code=symbol,
            days=days,
            coin_name=coin_name,
        )

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Historical data for '{symbol}' not found or unavailable",
        )

    return HistoryResponse(
        symbol=symbol.upper(),
        days=days,
        data=[HistoricalDataPoint(**point) for point in data],
    )
