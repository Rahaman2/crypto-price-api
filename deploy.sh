#!/bin/bash
set -euo pipefail

PROJECT_DIR="/var/www/crypto-price-api"
API_URL="https://crypto.matricmate.co.za"

echo "============================================"
echo " Crypto Price API - Deploy Script"
echo "============================================"

# Pull latest code
echo "[1/4] Pulling latest changes..."
cd "$PROJECT_DIR"
git pull origin main

# Create/activate virtual environment
echo "[2/4] Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install dependencies
echo "[3/4] Installing dependencies..."
pip install -r requirements.txt --quiet

# Restart PM2 process
echo "[4/4] Restarting PM2 process..."
pm2 restart crypto-price-api || pm2 start ecosystem.config.js

# Verify
sleep 3
pm2 status
echo ""
echo "Deploy complete. Verify at:"
echo "  API:      $API_URL/health"
echo "  Docs:     $API_URL/docs"
