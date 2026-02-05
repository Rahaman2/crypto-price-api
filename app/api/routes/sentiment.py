from fastapi import APIRouter, HTTPException
from app.models.schemas import FearGreedResponse
from app.services.fear_greed import fear_greed_service

router = APIRouter()


@router.get("", response_model=FearGreedResponse)
async def get_fear_greed():
    """
    Get the current Crypto Fear & Greed Index.

    Returns a value from 0-100:
    - 0-24: Extreme Fear
    - 25-49: Fear
    - 50-74: Greed
    - 75-100: Extreme Greed
    """
    data = await fear_greed_service.get_index()

    if not data:
        raise HTTPException(
            status_code=503,
            detail="Fear & Greed Index temporarily unavailable",
        )

    return FearGreedResponse(**data)
