# config.py
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY    = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BASE_URL   = os.getenv("BINANCE_BASE_URL", "https://testnet.binancefuture.com")

if not API_KEY or not API_SECRET:
    raise EnvironmentError(
        "Missing BINANCE_API_KEY or BINANCE_API_SECRET in your .env file."
    )