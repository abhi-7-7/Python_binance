# core/order_service.py
import importlib
import importlib.util

if importlib.util.find_spec("requests") is not None:
    requests = importlib.import_module("requests")
else:
    class RequestException(Exception):
        pass

    class HTTPError(Exception):
        def __init__(self, response=None):
            self.response = response

    requests = type(
        "requests",
        (),
        {"HTTPError": HTTPError, "RequestException": RequestException},
    )

from api.binance_client import BinanceClient
from core import error_handler, validator
from core.models import OrderRequest, OrderResult
from logger import get_logger

log = get_logger(__name__)


class OrderService:
    def __init__(self, api_key: str = None, api_secret: str = None, base_url: str = None):
        self.client = BinanceClient(
            api_key    = api_key,
            api_secret = api_secret,
            base_url   = base_url,
        )

    def place_market_order(self, symbol: str, side: str, quantity: float) -> OrderResult:
        request = self._validate(symbol, side, "MARKET", quantity, price=None)
        log.info("Placing MARKET order | symbol=%s side=%s qty=%s",
                 request.symbol, request.side, request.quantity)
        params = {
            "symbol":   request.symbol,
            "side":     request.side,
            "type":     "MARKET",
            "quantity": request.quantity,
        }
        return self._execute(request, params)

    def place_limit_order(self, symbol: str, side: str,
                          quantity: float, price: float) -> OrderResult:
        request = self._validate(symbol, side, "LIMIT", quantity, price)
        log.info("Placing LIMIT order | symbol=%s side=%s qty=%s price=%s",
                 request.symbol, request.side, request.quantity, request.price)
        params = {
            "symbol":      request.symbol,
            "side":        request.side,
            "type":        "LIMIT",
            "quantity":    request.quantity,
            "price":       request.price,
            "timeInForce": "GTC",
        }
        return self._execute(request, params)

    def _validate(self, symbol, side, order_type, quantity, price):
        return OrderRequest(
            symbol     = validator.validate_symbol(symbol),
            side       = validator.validate_side(side),
            order_type = validator.validate_order_type(order_type),
            quantity   = validator.validate_quantity(quantity),
            price      = validator.validate_price(price) if price is not None else None,
        )

    def _execute(self, request: OrderRequest, params: dict) -> OrderResult:
        try:
            raw = self.client.post_order(params)
        except requests.HTTPError as exc:
            log.error("Order FAILED | symbol=%s side=%s type=%s",
                      request.symbol, request.side, request.order_type)
            error_handler.handle_api_error(exc)
        except requests.RequestException as exc:
            log.error(
                "Network error while placing order | symbol=%s side=%s type=%s",
                request.symbol,
                request.side,
                request.order_type,
                exc_info=True,
            )
            raise RuntimeError("Network error while contacting Binance.") from exc

        result = self._map_response(raw, request)
        log.info("Order SUCCESS | id=%s symbol=%s side=%s type=%s qty=%s price=%s status=%s",
                 result.order_id, result.symbol, result.side, result.order_type,
                 result.executed_qty, result.avg_price, result.status)
        return result

    def _map_response(self, raw: dict, request: OrderRequest) -> OrderResult:
        quantity    = float(raw.get("origQty")   or raw.get("executedQty") or 0)
        avg_price   = float(raw.get("avgPrice")  or 0)
        limit_price = float(raw.get("price")     or 0)
        return OrderResult(
            order_id     = raw.get("orderId",     0),
            status       = raw.get("status",      "UNKNOWN"),
            symbol       = raw.get("symbol",      request.symbol),
            side         = raw.get("side",        request.side),
            order_type   = raw.get("type",        request.order_type),
            executed_qty = quantity,
            avg_price    = avg_price if avg_price > 0 else limit_price,
            timestamp    = raw.get("updateTime",  0),
        )