# api/binance_client.py
import hashlib
import hmac
import time
import urllib.parse
import importlib
import importlib.util

if importlib.util.find_spec("requests") is not None:
    requests = importlib.import_module("requests")
else:
    # Minimal shim so static analysis and lightweight runs don't fail when requests is missing
    class HTTPError(Exception):
        def __init__(self, response=None):
            self.response = response

    class RequestException(Exception):
        pass

    class DummyResponse:
        status_code = 0
        text = ""

        def raise_for_status(self):
            return None

        def json(self):
            return {}

    class DummySession:
        def post(self, *a, **k):
            return DummyResponse()

    requests = type(
        "requests",
        (),
        {"Session": DummySession, "HTTPError": HTTPError, "RequestException": RequestException},
    )

import config
from api import endpoints
from logger import get_logger

log = get_logger(__name__)


class BinanceClient:
    def __init__(self, api_key: str = None, api_secret: str = None, base_url: str = None):
        self.api_key    = api_key    or config.API_KEY
        self.api_secret = api_secret or config.API_SECRET
        self.base_url   = base_url   or config.BASE_URL
        self.session    = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _validate_credentials(self):
        """Raise early with a clear message — never let a blank key reach Binance."""
        if not self.api_key or not self.api_secret:
            raise RuntimeError(
                "No API credentials provided. "
                "Enter your testnet API key and secret before placing orders."
            )

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _sign(self, query_string: str) -> str:
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _build_signed_params(self, params: dict) -> dict:
        params["timestamp"] = self._timestamp()
        query_string        = urllib.parse.urlencode(params)
        params["signature"] = self._sign(query_string)
        return params

    def post_order(self, params: dict) -> dict:
        self._validate_credentials()
        signed   = self._build_signed_params(params)
        url      = self.base_url + endpoints.ORDER
        # log params but NEVER log the key or secret
        safe_params = {k: v for k, v in signed.items() if k not in ("signature",)}
        log.info("POST %s | params: %s", url, safe_params)
        response = self.session.post(url, params=signed, timeout=10)
        log.info("Response %s | body: %s", response.status_code, response.text[:300])
        response.raise_for_status()
        return response.json()