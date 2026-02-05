from fastapi import APIRouter
from app.models.schemas import TrendingResponse, TrendingCoin
from app.services.coingecko import coingecko_service

router = APIRouter()


@router.get("", response_model=TrendingResponse)
async def get_trending():
    """
    Get trending cryptocurrencies.

    Returns the top trending coins based on CoinGecko search data.
    """
    coins = await coingecko_service.get_trending()

    return TrendingResponse(
        coins=[TrendingCoin(**coin) for coin in coins]
    )
