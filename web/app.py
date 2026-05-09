# web/app.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util

if importlib.util.find_spec("flask") is not None:
    _flask = importlib.import_module("flask")
    Flask = _flask.Flask
    jsonify = _flask.jsonify
    request = _flask.request
    render_template = _flask.render_template
else:
    # Minimal Flask shim for static checks and lightweight runs
    class _DummyRequest:
        def get_json(self):
            return {}

    class Flask:
        def __init__(self, *a, **k):
            pass
        def route(self, *a, **k):
            def decorator(f):
                return f
            return decorator
        def run(self, *a, **k):
            return None

    def jsonify(obj):
        return obj

    request = _DummyRequest()

    def render_template(name, *a, **k):
        return f"Rendered {name}"
from core.order_service import OrderService

app = Flask(__name__)

LOG_FILE     = os.path.join("logs", "trades.log")
SKIP_PHRASES = ["POST https", "Response 200", "Response 401",
                "body:", '{"orderId', "Traceback"]


def _read_logs(n: int = 50) -> list:
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [
        l.strip() for l in lines
        if l.strip() and not any(p in l for p in SKIP_PHRASES)
    ][-n:]


def _log_stats() -> dict:
    lines = _read_logs(200)
    return {
        "total":   sum(1 for l in lines if "SUCCESS" in l or "FAILED" in l),
        "success": sum(1 for l in lines if "SUCCESS" in l),
        "failed":  sum(1 for l in lines if "FAILED"  in l),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stats")
def stats():
    return jsonify(_log_stats())


@app.route("/api/logs")
def logs():
    return jsonify({"logs": _read_logs()})


@app.route("/api/order", methods=["POST"])
def place_order():
    data = request.get_json()

    # Keys MUST come from the request body — never from .env
    api_key    = data.get("api_key",    "").strip()
    api_secret = data.get("api_secret", "").strip()
    base_url   = data.get("base_url",   "https://testnet.binancefuture.com").strip()

    if not api_key or not api_secret:
        return jsonify({"ok": False, "error": "API key and secret are required."}), 400

    order_type = data.get("type",     "MARKET").upper()
    symbol     = data.get("symbol",   "").strip()
    side       = data.get("side",     "").strip()

    try:
        quantity = float(data.get("quantity", 0))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Invalid quantity."}), 400

    try:
        svc = OrderService(api_key=api_key, api_secret=api_secret, base_url=base_url)

        if order_type == "MARKET":
            result = svc.place_market_order(symbol, side, quantity)
        else:
            try:
                price = float(data.get("price", 0))
            except (TypeError, ValueError):
                return jsonify({"ok": False, "error": "Invalid price."}), 400
            result = svc.place_limit_order(symbol, side, quantity, price)

        return jsonify({
            "ok":       True,
            "order_id": result.order_id,
            "status":   result.status,
            "symbol":   result.symbol,
            "side":     result.side,
            "type":     result.order_type,
            "qty":      result.executed_qty,
            "price":    result.avg_price,
        })

    except (ValueError, RuntimeError) as e:
        return jsonify({"ok": False, "error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)