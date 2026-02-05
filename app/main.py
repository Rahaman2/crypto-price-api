from fastapi import FastAPI
from app.config import get_settings
from app.api.routes import price, history, top, trending, sentiment

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="A simple API for getting cryptocurrency prices and market data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers
app.include_router(price.router, prefix="/price", tags=["Price"])
app.include_router(history.router, prefix="/history", tags=["History"])
app.include_router(top.router, prefix="/prices/top100", tags=["Top Coins"])
app.include_router(trending.router, prefix="/trending", tags=["Trending"])
app.include_router(sentiment.router, prefix="/fear-greed", tags=["Sentiment"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "name": settings.app_name,
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}
