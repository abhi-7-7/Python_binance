# core/validator.py
import re


VALID_SIDES = {"BUY", "SELL"}
VALID_TYPES = {"MARKET", "LIMIT"}

# Binance symbols are 2–12 uppercase letters/digits (e.g. BTCUSDT, ETHUSDT)
_SYMBOL_RE = re.compile(r"^[A-Z0-9]{2,12}$")


def validate_symbol(symbol: str) -> str:
    """
    Must be uppercase, 2–12 alphanumeric characters.
    Returns the cleaned symbol or raises ValueError.
    """
    cleaned = symbol.strip().upper()
    if not _SYMBOL_RE.match(cleaned):
        raise ValueError(
            f"Invalid symbol '{symbol}'. "
            "Use uppercase letters and digits only, e.g. BTCUSDT."
        )
    return cleaned


def validate_side(side: str) -> str:
    """Must be BUY or SELL (case-insensitive)."""
    cleaned = side.strip().upper()
    if cleaned not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be BUY or SELL."
        )
    return cleaned


def validate_order_type(order_type: str) -> str:
    """Must be MARKET or LIMIT (case-insensitive)."""
    cleaned = order_type.strip().upper()
    if cleaned not in VALID_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be MARKET or LIMIT."
        )
    return cleaned


def validate_quantity(quantity: float) -> float:
    """
    Must be a positive number.
    Binance Futures minimum for BTCUSDT is 0.001.
    We enforce 3 decimal places max to avoid precision errors.
    """
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")
    rounded = round(quantity, 3)
    if rounded == 0:
        raise ValueError("Quantity is too small after rounding to 3 decimal places.")
    return rounded


def validate_price(price: float) -> float:
    """
    Must be a positive number.
    Required for LIMIT orders only.
    """
    if price <= 0:
        raise ValueError("Price must be greater than zero.")
    return round(price, 2)