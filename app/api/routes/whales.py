from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import httpx

router = APIRouter()

# Using blockchain.info and other free APIs for whale data
WHALE_THRESHOLD_BTC = 100  # BTC
WHALE_THRESHOLD_USD = 1000000  # $1M


@router.get("/transactions")
async def get_whale_transactions(
    limit: int = Query(default=10, ge=1, le=50, description="Number of transactions"),
    min_value_usd: int = Query(default=1000000, ge=100000, description="Minimum transaction value in USD"),
):
    """
    Get recent large cryptocurrency transactions (whale movements).

    - **limit**: Number of transactions to return
    - **min_value_usd**: Minimum transaction value in USD (default: $1,000,000)

    Data sourced from public blockchain explorers.
    """
    transactions = []

    try:
        # Fetch latest BTC blocks and large transactions
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Get current BTC price
            price_resp = await client.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
            btc_price = price_resp.json().get("bitcoin", {}).get("usd", 50000)

            # Get latest unconfirmed transactions from blockchain.info
            response = await client.get(
                "https://blockchain.info/unconfirmed-transactions?format=json",
                headers={"User-Agent": "CryptoPriceAPI/1.0"}
            )

            if response.status_code == 200:
                data = response.json()
                txs = data.get("txs", [])

                for tx in txs:
                    # Calculate total output value
                    total_btc = sum(out.get("value", 0) for out in tx.get("out", [])) / 100000000
                    total_usd = total_btc * btc_price

                    if total_usd >= min_value_usd:
                        transactions.append({
                            "hash": tx.get("hash"),
                            "blockchain": "bitcoin",
                            "symbol": "BTC",
                            "amount": round(total_btc, 4),
                            "amount_usd": round(total_usd, 2),
                            "timestamp": tx.get("time"),
                            "from_address": tx.get("inputs", [{}])[0].get("prev_out", {}).get("addr", "Unknown"),
                            "to_address": tx.get("out", [{}])[0].get("addr", "Unknown"),
                        })

                        if len(transactions) >= limit:
                            break

    except Exception as e:
        # Return empty if API fails
        pass

    return {
        "count": len(transactions),
        "min_value_usd": min_value_usd,
        "blockchain": "bitcoin",
        "transactions": transactions,
        "note": "Real-time whale transactions from Bitcoin blockchain"
    }


@router.get("/stats")
async def get_whale_stats():
    """
    Get whale activity statistics for the last 24 hours.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get BTC stats
            response = await client.get("https://api.blockchain.info/stats")

            if response.status_code == 200:
                data = response.json()
                return {
                    "blockchain": "bitcoin",
                    "stats": {
                        "total_btc_sent_24h": round(data.get("total_btc_sent", 0) / 100000000, 2),
                        "n_transactions_24h": data.get("n_tx", 0),
                        "n_blocks_mined_24h": data.get("n_blocks_mined", 0),
                        "minutes_between_blocks": round(data.get("minutes_between_blocks", 0), 2),
                        "hash_rate": data.get("hash_rate", 0),
                        "difficulty": data.get("difficulty", 0),
                        "market_price_usd": data.get("market_price_usd", 0),
                    }
                }
    except Exception:
        pass

    raise HTTPException(status_code=503, detail="Unable to fetch whale statistics")
