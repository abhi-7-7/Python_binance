# cli/commands.py
import importlib
import importlib.util

if importlib.util.find_spec("click") is not None:
    click = importlib.import_module("click")
else:
    # Lightweight click shim for environments without click installed (keeps CLI definitions importable)
    class Choice:
        def __init__(self, options, case_sensitive=True):
            self.options = options

    class BadParameter(Exception):
        pass

    def _command_decorator(name=None):
        def decorator(f):
            return f
        return decorator

    def group():
        def decorator(f):
            f.command = _command_decorator
            return f
        return decorator

    def option(*a, **k):
        def decorator(f):
            return f
        return decorator

    def command(name=None):
        return _command_decorator(name)

    def secho(msg, fg=None, err=False):
        print(msg)

    click = type("click", (), {
        "Choice": Choice,
        "BadParameter": BadParameter,
        "group": group,
        "option": option,
        "command": command,
        "secho": secho,
    })

from core.order_service import OrderService
from logger import get_logger

log = get_logger(__name__)


def _print_request_summary(symbol: str, side: str, order_type: str, quantity: float, price=None) -> None:
    price_str = "market" if price is None else f"{price}"
    click.secho("Order request summary:")
    click.secho(f"  Symbol: {symbol.strip().upper()}")
    click.secho(f"  Side: {side.strip().upper()}")
    click.secho(f"  Type: {order_type}")
    click.secho(f"  Quantity: {quantity}")
    click.secho(f"  Price: {price_str}")


@click.group()
def cli():
    """
    Binance Futures Testnet — CLI Order Tool

    Place MARKET and LIMIT orders directly from the terminal.
    All trades execute on the testnet (no real funds).
    """


@cli.command("market")
@click.option("--symbol",   required=True, help="Trading pair, e.g. BTCUSDT")
@click.option("--side",     required=True, type=click.Choice(["BUY", "SELL"], case_sensitive=False), help="BUY or SELL")
@click.option("--quantity", required=True, type=float, help="Amount of base asset, e.g. 0.001")
def market_order(symbol: str, side: str, quantity: float):
    """
    Place a MARKET order — executes immediately at the current market price.

    \b
    Example:
        python main.py market --symbol BTCUSDT --side BUY --quantity 0.001
    """
    service = OrderService()
    try:
        _print_request_summary(symbol, side, "MARKET", quantity)
        result = service.place_market_order(symbol, side, quantity)
        click.secho(result.display(), fg="green")
    except ValueError as e:
        log.warning("Validation error: %s", e)
        raise click.BadParameter(str(e))
    except RuntimeError as e:
        log.error("Order failed: %s", e)
        click.secho("Order failed.", fg="red", err=True)
        click.secho(f"\n  Error: {e}\n", fg="red", err=True)
        raise SystemExit(1)


@cli.command("limit")
@click.option("--symbol",   required=True, help="Trading pair, e.g. BTCUSDT")
@click.option("--side",     required=True, type=click.Choice(["BUY", "SELL"], case_sensitive=False), help="BUY or SELL")
@click.option("--quantity", required=True, type=float, help="Amount of base asset, e.g. 0.001")
@click.option("--price",    required=True, type=float, help="Target price for the order")
def limit_order(symbol: str, side: str, quantity: float, price: float):
    """
    Place a LIMIT order — rests on the book until your price is matched.

    \b
    Example:
        python main.py limit --symbol BTCUSDT --side BUY --quantity 0.001 --price 50000
    """
    service = OrderService()
    try:
        _print_request_summary(symbol, side, "LIMIT", quantity, price)
        result = service.place_limit_order(symbol, side, quantity, price)
        click.secho(result.display(), fg="green")
    except ValueError as e:
        log.warning("Validation error: %s", e)
        raise click.BadParameter(str(e))
    except RuntimeError as e:
        log.error("Order failed: %s", e)
        click.secho("Order failed.", fg="red", err=True)
        click.secho(f"\n  Error: {e}\n", fg="red", err=True)
        raise SystemExit(1)