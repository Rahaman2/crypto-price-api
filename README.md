# Crypto Price API

A fast, modular FastAPI-based cryptocurrency price API. Perfect for trading bots, portfolio trackers, and crypto applications.

## Features

- **Real-time prices** via Binance (primary) + CoinGecko (fallback)
- **Historical OHLC data** up to 365 days
- **Top 100 coins** by market cap
- **Trending coins** from CoinGecko
- **Fear & Greed Index** market sentiment

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd crypto-price-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`

## API Endpoints

### Get Price
```bash
GET /price/{symbol}
```
Returns current price with 24h change. Uses Binance (faster) with CoinGecko fallback.

**Example:**
```bash
curl http://localhost:8000/price/btc
```
```json
{
  "symbol": "BTC",
  "name": "Bitcoin",
  "price_usd": 65000.50,
  "price_change_24h": -2.5,
  "volume_24h": 25000000000,
  "last_updated": "2024-01-15T10:30:00Z",
  "source": "binance"
}
```

### Get Historical Data
```bash
GET /history/{symbol}?days=30
```
Returns OHLC data for the specified number of days (1-365).

**Example:**
```bash
curl "http://localhost:8000/history/eth?days=7"
```
```json
{
  "symbol": "ETH",
  "days": 7,
  "data": [
    {
      "date": "2024-01-15",
      "open": 2500.00,
      "high": 2600.00,
      "low": 2450.00,
      "close": 2550.00
    }
  ]
}
```

### Get Top 100 Coins
```bash
GET /prices/top100?limit=100
```
Returns top coins ranked by market cap. Adjust limit (1-250).

**Example:**
```bash
curl "http://localhost:8000/prices/top100?limit=10"
```

### Get Trending Coins
```bash
GET /trending
```
Returns currently trending coins based on search activity.

**Example:**
```bash
curl http://localhost:8000/trending
```

### Get Fear & Greed Index
```bash
GET /fear-greed
```
Returns the current market sentiment index (0-100).

**Example:**
```bash
curl http://localhost:8000/fear-greed
```
```json
{
  "value": 35,
  "classification": "Fear",
  "timestamp": "2024-01-15T00:00:00Z"
}
```

## Data Sources

| Source | Used For | Rate Limit |
|--------|----------|------------|
| **Binance** | Real-time prices (primary) | 1200 req/min |
| **CoinGecko** | Prices (fallback), top coins, trending, history | 10-50 req/min |
| **CoinMarketCap** | Historical data (via cryptoCMD) | Varies |
| **Alternative.me** | Fear & Greed Index | Unlimited |

## Project Structure

```
crypto-price-api/
├── app/
│   ├── main.py           # FastAPI app
│   ├── config.py         # Settings
│   ├── api/routes/       # Endpoint handlers
│   │   ├── price.py      # /price
│   │   ├── history.py    # /history
│   │   ├── top.py        # /prices/top100
│   │   ├── trending.py   # /trending
│   │   └── sentiment.py  # /fear-greed
│   ├── services/         # External API clients
│   │   ├── binance.py    # Binance API
│   │   ├── coingecko.py  # CoinGecko API
│   │   ├── coinmarketcap.py
│   │   └── fear_greed.py
│   └── models/
│       └── schemas.py    # Pydantic models
├── requirements.txt
└── README.md
```

## API Documentation

Interactive docs available when running:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Deployment

### RapidAPI
This API is designed for RapidAPI deployment. RapidAPI handles:
- Rate limiting
- API key authentication
- Pricing tiers
- Analytics

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## License

MIT
