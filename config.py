# config.py
import os
import importlib
import importlib.util

if importlib.util.find_spec("dotenv") is not None:
    load_dotenv = importlib.import_module("dotenv").load_dotenv
else:
    # Fallback when python-dotenv isn't installed (helps static checks and lightweight runs)
    def load_dotenv(*a, **k):
        return None

load_dotenv()

API_KEY    = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BASE_URL   = os.getenv("BINANCE_BASE_URL", "https://testnet.binancefuture.com")

if not API_KEY or not API_SECRET:
    raise EnvironmentError(
        "Missing BINANCE_API_KEY or BINANCE_API_SECRET in your .env file."
    )