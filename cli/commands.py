# cli/commands.py
import click

from core.order_service import OrderService
from logger import get_logger

log = get_logger(__name__)


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
        result = service.place_market_order(symbol, side, quantity)
        click.secho(result.display(), fg="green")
    except ValueError as e:
        log.warning("Validation error: %s", e)
        raise click.BadParameter(str(e))
    except RuntimeError as e:
        log.error("Order failed: %s", e)
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
        result = service.place_limit_order(symbol, side, quantity, price)
        click.secho(result.display(), fg="green")
    except ValueError as e:
        log.warning("Validation error: %s", e)
        raise click.BadParameter(str(e))
    except RuntimeError as e:
        log.error("Order failed: %s", e)
        click.secho(f"\n  Error: {e}\n", fg="red", err=True)
        raise SystemExit(1)