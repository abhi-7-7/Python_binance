# core/models.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class OrderRequest:
    """Validated, sanitised order parameters ready for the API layer."""
    symbol:     str
    side:       str            # "BUY" | "SELL"
    order_type: str            # "MARKET" | "LIMIT"
    quantity:   float
    price:      Optional[float] = None   # required for LIMIT, None for MARKET


@dataclass
class OrderResult:
    """Normalised response returned to the CLI layer."""
    order_id:     int
    status:       str
    symbol:       str
    side:         str
    order_type:   str
    executed_qty: float
    avg_price:    float
    timestamp:    int          # Unix ms from Binance

    def display(self) -> str:
        """Human-readable summary for terminal output."""
        price_str = f"${self.avg_price:,.4f}" if self.avg_price else "pending"
        return (
            f"\n{'─'*44}\n"
            f"  Order placed successfully\n"
            f"{'─'*44}\n"
            f"  Order ID   : {self.order_id}\n"
            f"  Symbol     : {self.symbol}\n"
            f"  Side       : {self.side}\n"
            f"  Type       : {self.order_type}\n"
            f"  Quantity   : {self.executed_qty}\n"
            f"  Avg Price  : {price_str}\n"
            f"  Status     : {self.status}\n"
            f"{'─'*44}\n"
        )