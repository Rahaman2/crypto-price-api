from fastapi import APIRouter, Query
from app.models.schemas import TopCoinsResponse, TopCoin
from app.services.coingecko import coingecko_service

router = APIRouter()


@router.get("", response_model=TopCoinsResponse)
async def get_top_coins(
    limit: int = Query(default=100, ge=1, le=250, description="Number of coins to return"),
):
    """
    Get top cryptocurrencies by market cap.

    - **limit**: Number of coins to return (1-250, default: 100)
    """
    coins = await coingecko_service.get_top_coins(limit=limit)

    return TopCoinsResponse(
        coins=[TopCoin(**coin) for coin in coins]
    )
