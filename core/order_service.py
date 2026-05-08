# core/order_service.py
import requests

from api.binance_client import BinanceClient
from core import error_handler, validator
from core.models import OrderRequest, OrderResult
from logger import get_logger

log = get_logger(__name__)


class OrderService:
    """
    Orchestrates the full order lifecycle:
      1. Validate inputs
      2. Build API parameters
      3. Call BinanceClient
      4. Map raw response → OrderResult
      5. Log every outcome

    This is the only class that touches both the core and API layers.
    The CLI layer talks exclusively to this class.
    """

    def __init__(self):
        self.client = BinanceClient()

    # ------------------------------------------------------------------ #
    #  Public interface                                                    #
    # ------------------------------------------------------------------ #

    def place_market_order(self, symbol: str, side: str, quantity: float) -> OrderResult:
        """
        Place a MARKET order that executes immediately at the best price.

        Args:
            symbol:   Trading pair, e.g. "BTCUSDT"
            side:     "BUY" or "SELL"
            quantity: Amount of base asset to trade

        Returns:
            OrderResult with execution details

        Raises:
            ValueError:   on invalid inputs (before any API call)
            RuntimeError: on Binance API rejection
        """
        request = self._validate(symbol, side, "MARKET", quantity, price=None)

        log.info(
            "Placing MARKET order | symbol=%s side=%s qty=%s",
            request.symbol, request.side, request.quantity,
        )

        params = {
            "symbol":   request.symbol,
            "side":     request.side,
            "type":     "MARKET",
            "quantity": request.quantity,
        }

        return self._execute(request, params)

    def place_limit_order(
        self, symbol: str, side: str, quantity: float, price: float
    ) -> OrderResult:
        """
        Place a LIMIT order that rests on the book until the price is met.

        Args:
            symbol:   Trading pair, e.g. "BTCUSDT"
            side:     "BUY" or "SELL"
            quantity: Amount of base asset to trade
            price:    Target execution price

        Returns:
            OrderResult with order details (status will be NEW until filled)

        Raises:
            ValueError:   on invalid inputs
            RuntimeError: on Binance API rejection
        """
        request = self._validate(symbol, side, "LIMIT", quantity, price)

        log.info(
            "Placing LIMIT order | symbol=%s side=%s qty=%s price=%s",
            request.symbol, request.side, request.quantity, request.price,
        )

        params = {
            "symbol":      request.symbol,
            "side":        request.side,
            "type":        "LIMIT",
            "quantity":    request.quantity,
            "price":       request.price,
            "timeInForce": "GTC",   # Good Till Cancelled
        }

        return self._execute(request, params)

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _validate(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None,
    ) -> OrderRequest:
        """Run all validators and return a clean OrderRequest."""
        return OrderRequest(
            symbol     = validator.validate_symbol(symbol),
            side       = validator.validate_side(side),
            order_type = validator.validate_order_type(order_type),
            quantity   = validator.validate_quantity(quantity),
            price      = validator.validate_price(price) if price is not None else None,
        )

    def _execute(self, request: OrderRequest, params: dict) -> OrderResult:
        """Call the API client, handle errors, map to OrderResult."""
        try:
            raw = self.client.post_order(params)
        except requests.HTTPError as exc:
            log.error(
                "Order FAILED | symbol=%s side=%s type=%s",
                request.symbol, request.side, request.order_type,
            )
            error_handler.handle_api_error(exc)   # always raises RuntimeError

        result = self._map_response(raw, request)

        log.info(
            "Order SUCCESS | id=%s symbol=%s side=%s type=%s qty=%s price=%s status=%s",
            result.order_id, result.symbol, result.side,
            result.order_type, result.executed_qty,
            result.avg_price, result.status,
        )

        return result

    def _map_response(self, raw: dict, request: OrderRequest) -> OrderResult:
        """Convert the raw Binance JSON dict into a typed OrderResult."""
        # origQty = what you asked for; executedQty = what filled so far (0 on placement)
        quantity = float(raw.get("origQty") or raw.get("executedQty") or 0)

        # avgPrice is 0 until filled — fall back to the limit price if set
        avg_price = float(raw.get("avgPrice") or raw.get("price") or 0)

        return OrderResult(
            order_id     = raw.get("orderId", 0),
            status       = raw.get("status", "UNKNOWN"),
            symbol       = raw.get("symbol", request.symbol),
            side         = raw.get("side", request.side),
            order_type   = raw.get("type", request.order_type),
            executed_qty = quantity,
            avg_price    = avg_price,
            timestamp    = raw.get("updateTime", 0),
    )