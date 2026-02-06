from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import mplfinance as mpf
import pandas as pd
import io
from app.services.coingecko import coingecko_service
from app.services.coinmarketcap import coinmarketcap_service

router = APIRouter()


@router.get("/{symbol}")
async def get_candlestick_chart(
    symbol: str,
    days: int = Query(default=30, ge=7, le=365, description="Number of days (7-365)"),
    style: str = Query(default="nightclouds", description="Chart style: nightclouds, yahoo, charles, mike, binance"),
    width: int = Query(default=1200, ge=400, le=1920, description="Image width in pixels"),
    height: int = Query(default=600, ge=300, le=1080, description="Image height in pixels"),
):
    """
    Generate a candlestick chart image for a cryptocurrency.

    - **symbol**: Coin symbol or ID (e.g., "bitcoin", "ethereum", "btc")
    - **days**: Number of days of history (7-365, default: 30)
    - **style**: Chart style theme
    - **width**: Image width in pixels (400-1920)
    - **height**: Image height in pixels (300-1080)

    Returns a PNG image of the candlestick chart.
    """
    # Get coin ID
    coin_id = symbol.lower()
    if len(symbol) <= 5:
        found_id = await coingecko_service.search_coin(symbol)
        if found_id:
            coin_id = found_id

    # Fetch historical data
    data = await coingecko_service.get_historical_data(coin_id=coin_id, days=days)

    if not data:
        data = coinmarketcap_service.get_historical_data(
            coin_code=symbol,
            days=days,
        )

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Historical data for '{symbol}' not found",
        )

    # Convert to DataFrame for mplfinance
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })

    # Select only required columns
    df = df[['Open', 'High', 'Low', 'Close']]
    df = df.sort_index()

    # Define custom styles
    styles = {
        'nightclouds': mpf.make_mpf_style(
            base_mpf_style='nightclouds',
            rc={'font.size': 10}
        ),
        'yahoo': mpf.make_mpf_style(
            base_mpf_style='yahoo',
            rc={'font.size': 10}
        ),
        'charles': mpf.make_mpf_style(
            base_mpf_style='charles',
            rc={'font.size': 10}
        ),
        'mike': mpf.make_mpf_style(
            base_mpf_style='mike',
            rc={'font.size': 10}
        ),
        'binance': mpf.make_mpf_style(
            base_mpf_style='binance',
            rc={'font.size': 10}
        ),
    }

    chart_style = styles.get(style, styles['nightclouds'])

    # Generate chart to bytes buffer
    buf = io.BytesIO()

    fig, axes = mpf.plot(
        df,
        type='candle',
        style=chart_style,
        title=f'{symbol.upper()} - {days} Day Candlestick Chart',
        ylabel='Price (USD)',
        figsize=(width/100, height/100),
        returnfig=True,
    )

    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={
            "Content-Disposition": f"inline; filename={symbol.lower()}_chart.png"
        }
    )
