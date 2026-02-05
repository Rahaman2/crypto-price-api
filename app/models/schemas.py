from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PriceResponse(BaseModel):
    symbol: str
    name: Optional[str] = None
    price_usd: float
    price_change_24h: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    last_updated: Optional[datetime] = None
    source: str = "unknown"  # "binance" or "coingecko"


class HistoricalDataPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None
    market_cap: Optional[float] = None


class HistoryResponse(BaseModel):
    symbol: str
    days: int
    data: list[HistoricalDataPoint]


class TopCoin(BaseModel):
    rank: int
    symbol: str
    name: str
    price_usd: float
    market_cap: Optional[float] = None
    price_change_24h: Optional[float] = None


class TopCoinsResponse(BaseModel):
    coins: list[TopCoin]


class TrendingCoin(BaseModel):
    symbol: str
    name: str
    market_cap_rank: Optional[int] = None
    price_btc: Optional[float] = None


class TrendingResponse(BaseModel):
    coins: list[TrendingCoin]


class FearGreedResponse(BaseModel):
    value: int
    classification: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    detail: str
