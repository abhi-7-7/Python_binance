# streamlit_app.py
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import importlib
import importlib.util

if importlib.util.find_spec("streamlit") is not None:
    st = importlib.import_module("streamlit")
else:
    # Minimal Streamlit shim so the app can be imported without installing streamlit
    class _DummyColumn:
        def metric(self, *a, **k):
            return None
        def markdown(self, *a, **k):
            return None
        def number_input(self, *a, **k):
            return k.get("value", 0)
        def radio(self, *a, **k):
            return a[1][0] if len(a) > 1 else None
        def text_input(self, *a, **k):
            return k.get("value", "")
        def button(self, *a, **k):
            return False

    class _DummySpinner:
        def __init__(self, msg=""):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False

    class _DummySt:
        column_config = type("c", (), {"TextColumn": lambda *a, **k: None})
        def set_page_config(self, *a, **k):
            return None
        def markdown(self, *a, **k):
            return None
        def caption(self, *a, **k):
            return None
        def divider(self, *a, **k):
            return None
        def columns(self, *a, **k):
            if a and isinstance(a[0], int):
                n = a[0]
            elif a and isinstance(a[0], (list, tuple)):
                n = len(a[0])
            else:
                n = 1
            return tuple(_DummyColumn() for _ in range(n))
        def metric(self, *a, **k):
            return None
        def radio(self, *a, **k):
            return a[1][0] if len(a) > 1 else None
        def text_input(self, *a, **k):
            return k.get("value", "")
        def number_input(self, *a, **k):
            return k.get("value", 0)
        def button(self, *a, **k):
            return False
        def spinner(self, *a, **k):
            return _DummySpinner()
        def success(self, *a, **k):
            return None
        def error(self, *a, **k):
            return None
        def info(self, *a, **k):
            return None
        def dataframe(self, *a, **k):
            return None
        def rerun(self, *a, **k):
            return None

    st = _DummySt()

if importlib.util.find_spec("pandas") is not None:
    pd = importlib.import_module("pandas")
else:
    pd = type("pd", (), {"DataFrame": lambda data: data})
from datetime import datetime
from core.order_service import OrderService

st.set_page_config(
    page_title="Binance Futures",
    page_icon="📈",
    layout="wide",
)

LOG_FILE     = os.path.join("logs", "trades.log")
SKIP_PHRASES = ["POST https", "Response 200", "Response 401", "body:", '{"orderId']


# ── helpers ───────────────────────────────────────────────────────────────────
def get_service():
    return OrderService()


def read_logs(n=30):
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        return [
            l.strip() for l in lines
            if l.strip() and not any(p in l for p in SKIP_PHRASES)
        ][-n:]
    except Exception:
        return []


def log_stats():
    lines = read_logs(500)
    return {
        "total":   sum(1 for l in lines if "SUCCESS" in l or "FAILED" in l),
        "success": sum(1 for l in lines if "SUCCESS" in l),
        "failed":  sum(1 for l in lines if "FAILED"  in l),
    }


def parse_orders_from_log() -> list:
    """
    Parse every successful order from trades.log.
    Works for both CLI and UI orders — single source of truth.
    """
    orders = []
    if not os.path.exists(LOG_FILE):
        return orders
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                if "Order SUCCESS" not in line:
                    continue

                def extract(key):
                    try:
                        parts = line.split("|")[-1].split()
                        match = [p for p in parts if p.startswith(f"{key}=")]
                        return match[0].split("=")[1] if match else "—"
                    except Exception:
                        return "—"

                raw_price = extract("price")
                try:
                    price_val = float(raw_price)
                    price_str = f"${price_val:,.2f}" if price_val > 0 else "market"
                except Exception:
                    price_str = "market"

                orders.append({
                    "Time":     line.split("|")[0].strip(),
                    "Order ID": extract("id"),
                    "Symbol":   extract("symbol"),
                    "Type":     extract("type"),
                    "Side":     extract("side"),
                    "Qty":      extract("qty"),
                    "Price":    price_str,
                    "Status":   extract("status"),
                })
    except Exception:
        pass
    return list(reversed(orders))


def colour_log(line):
    c = (
        "#4ade80" if "SUCCESS" in line else
        "#f87171" if "FAILED"  in line else
        "#fbbf24" if "WARNING" in line else
        "#93c5fd"
    )
    parts = line.split(" | ")
    short = f"{parts[0]}  {parts[-1]}" if len(parts) >= 4 else line
    return (
        f'<span style="color:{c};font-family:monospace;'
        f'font-size:12px;line-height:1.9">{short}</span>'
    )


# ── header ────────────────────────────────────────────────────────────────────
st.markdown("## 📈 Binance Futures Dashboard")
st.caption("Binance Futures Testnet — no real funds at risk.")
st.divider()

# ── stats ─────────────────────────────────────────────────────────────────────
stats = log_stats()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total orders", stats["total"])
c2.metric("Successful",   stats["success"])
c3.metric("Failed",       stats["failed"])
c4.metric("Log file",     "trades.log")

st.divider()

# ── form + history ────────────────────────────────────────────────────────────
left, right = st.columns([1, 2], gap="large")

with left:
    st.markdown("### Place order")

    order_type = st.radio("Order type", ["MARKET", "LIMIT"], horizontal=True)
    side       = st.radio("Side",       ["BUY",    "SELL"],  horizontal=True)
    symbol     = st.text_input("Symbol", value="BTCUSDT").upper().strip()
    quantity   = st.number_input(
        "Quantity",
        min_value=0.001,
        value=0.001,
        step=0.001,
        format="%.3f",
    )

    price = None
    if order_type == "LIMIT":
        price = st.number_input(
            "Limit price (USDT)",
            min_value=1.0,
            value=50000.0,
            step=100.0,
        )

    st.markdown("")

    if st.button(
        f"{'🟢' if side == 'BUY' else '🔴'}  Place {order_type.lower()} order",
        type="primary",
        use_container_width=True,
    ):
        with st.spinner("Sending to Binance…"):
            try:
                svc = get_service()

                if order_type == "MARKET":
                    result = svc.place_market_order(symbol, side, quantity)
                else:
                    result = svc.place_limit_order(symbol, side, quantity, price)

                st.success(
                    f"✓  Order **#{result.order_id}** placed — `{result.status}`"
                )
                st.rerun()

            except ValueError as e:
                st.error(f"Validation: {e}")
            except RuntimeError as e:
                st.error(f"API error: {e}")
            except Exception as e:
                st.error(f"Error: {e}")

with right:
    st.markdown("### Order history")

    r1, r2 = st.columns([4, 1])
    with r2:
        if st.button("↻ Refresh", use_container_width=True):
            st.rerun()

    all_orders = parse_orders_from_log()

    if not all_orders:
        st.info("No orders in log yet. Place an order above or via the CLI.")
    else:
        df = pd.DataFrame(all_orders)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Time":     st.column_config.TextColumn(width="medium"),
                "Order ID": st.column_config.TextColumn(width="medium"),
                "Type":     st.column_config.TextColumn(width="small"),
                "Side":     st.column_config.TextColumn(width="small"),
                "Qty":      st.column_config.TextColumn(width="small"),
                "Price":    st.column_config.TextColumn(width="small"),
                "Status":   st.column_config.TextColumn(width="small"),
            },
        )

st.divider()

# ── live log ──────────────────────────────────────────────────────────────────
lc, rc = st.columns([5, 1])
lc.markdown("### Live log")
with rc:
    st.markdown("<div style='padding-top:28px'>", unsafe_allow_html=True)
    if st.button("↻ Refresh log", use_container_width=True):
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

logs = read_logs(30)

if not logs:
    st.caption("No activity yet.")
else:
    st.markdown(
        '<div style="background:#111;border-radius:10px;padding:16px 18px;'
        'max-height:240px;overflow-y:auto;line-height:1.9">'
        + "<br>".join(colour_log(l) for l in reversed(logs))
        + "</div>",
        unsafe_allow_html=True,
    )

st.divider()
st.caption(
    "Binance Futures CLI Dashboard  ·  Testnet only  ·  "
    "All orders logged to logs/trades.log"
)