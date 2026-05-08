# api/binance_client.py
import hashlib
import hmac
import time
import urllib.parse

import requests

import config
from api import endpoints
from logger import get_logger

log = get_logger(__name__)


class BinanceClient:
    """
    Low-level Binance Futures API client.

    Responsibilities:
      - Attach timestamp + HMAC-SHA256 signature to every signed request
      - Set the X-MBX-APIKEY header
      - Return raw JSON; raise requests.HTTPError on non-2xx responses

    This class knows nothing about order types or business rules.
    """

    def __init__(self):
        self.base_url   = config.BASE_URL
        self.api_key    = config.API_KEY
        self.api_secret = config.API_SECRET
        self.session    = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _timestamp(self) -> int:
        """Current Unix time in milliseconds (required by Binance)."""
        return int(time.time() * 1000)

    def _sign(self, query_string: str) -> str:
        """HMAC-SHA256 signature over the query string."""
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _build_signed_params(self, params: dict) -> dict:
        """
        Add timestamp, compute signature, return complete params dict.
        The signature must be the LAST parameter in the query string.
        """
        params["timestamp"] = self._timestamp()
        query_string        = urllib.parse.urlencode(params)
        params["signature"] = self._sign(query_string)
        return params

    # ------------------------------------------------------------------ #
    #  Public methods                                                      #
    # ------------------------------------------------------------------ #

    def post_order(self, params: dict) -> dict:
        """
        POST a new order to Binance Futures.

        Args:
            params: Dict of order parameters (symbol, side, type, etc.)
                    Do NOT include timestamp or signature — added here.

        Returns:
            Parsed JSON response dict from Binance.

        Raises:
            requests.HTTPError: on any non-2xx HTTP response.
        """
        signed = self._build_signed_params(params)
        url    = self.base_url + endpoints.ORDER

        log.info("POST %s | params: %s", url, {k: v for k, v in signed.items() if k != "signature"})

        response = self.session.post(url, params=signed, timeout=10)

        log.info("Response %s | body: %s", response.status_code, response.text[:500])

        response.raise_for_status()
        return response.json()