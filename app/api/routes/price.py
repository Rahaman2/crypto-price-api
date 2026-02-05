from fastapi import APIRouter, HTTPException
from app.models.schemas import PriceResponse
from app.services.binance import binance_service
from app.services.coingecko import coingecko_service

router = APIRouter()


@router.get("/{symbol}", response_model=PriceResponse)
async def get_price(symbol: str):
    """
    Get current price for a cryptocurrency.

    - **symbol**: Coin symbol (e.g., "btc", "eth", "sol", "bitcoin")

    Uses Binance as primary source (faster, real-time), falls back to CoinGecko.
    """
    # Try Binance first (primary source - faster, real-time)
    price_data = await binance_service.get_price(symbol)

    if price_data:
        # Binance doesn't provide coin name, try to get it from CoinGecko
        if not price_data.get("name"):
            coin_id = await coingecko_service.search_coin(symbol)
            if coin_id:
                cg_data = await coingecko_service.get_price(coin_id)
                if cg_data:
                    price_data["name"] = cg_data.get("name")
        return PriceResponse(**price_data)

    # Fallback to CoinGecko
    price_data = await coingecko_service.get_price(symbol.lower())

    if not price_data:
        # Try searching by symbol
        coin_id = await coingecko_service.search_coin(symbol)
        if coin_id:
            price_data = await coingecko_service.get_price(coin_id)

    if not price_data:
        raise HTTPException(status_code=404, detail=f"Coin '{symbol}' not found")

    price_data["source"] = "coingecko"
    return PriceResponse(**price_data)
