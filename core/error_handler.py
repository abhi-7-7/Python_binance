# core/error_handler.py
import requests

from logger import get_logger

log = get_logger(__name__)

# Binance Futures error code → friendly message
_BINANCE_ERRORS: dict[int, str] = {
    -1000: "Unknown error from Binance. Try again.",
    -1001: "Connection to Binance timed out. Check your internet.",
    -1002: "Unauthorized — check your API key in .env.",
    -1003: "Rate limit hit — too many requests. Wait a moment.",
    -1013: "Invalid quantity — too small or precision is wrong.",
    -1021: "Timestamp out of sync. Check your system clock.",
    -1100: "Invalid parameter format sent to Binance.",
    -1111: "Quantity precision error — use fewer decimal places.",
    -1121: "Invalid trading symbol. Example: BTCUSDT",
    -2010: "Order would immediately trigger — adjust your price.",
    -2019: "Insufficient margin. Add funds on the testnet.",
    -4003: "Quantity is below the minimum allowed for this symbol.",
    -4061: "Order side is not supported for this symbol.",
}


def handle_api_error(exc: requests.HTTPError) -> None:
    """
    Parse a Binance HTTPError response, log it, and raise a clean
    RuntimeError with a human-readable message.

    Usage:
        except requests.HTTPError as e:
            handle_api_error(e)   # always raises RuntimeError
    """
    raw_message = "Binance API error."
    code        = None

    try:
        body    = exc.response.json()
        code    = body.get("code")
        raw_message = body.get("msg", raw_message)
    except Exception:
        pass   # response wasn't JSON — use fallback

    friendly = _BINANCE_ERRORS.get(code, raw_message)

    log.error(
        "Binance API error | HTTP %s | code=%s | msg=%s",
        exc.response.status_code if exc.response is not None else "?",
        code,
        raw_message,
    )

    raise RuntimeError(friendly)