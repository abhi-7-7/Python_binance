# Binance Futures Testnet Trading Bot

Small Python app that places MARKET and LIMIT orders on Binance Futures Testnet (USDT-M). It uses direct REST calls via `requests` and keeps a clean, reusable structure with validation, logging, and error handling.

## Features
- CLI for MARKET and LIMIT orders (BUY and SELL)
- Input validation for symbol, side, order type, quantity, and price
- Structured layers: CLI, service, API client
- Logging of requests, responses, and errors to logs/trades.log
- Optional UI: Streamlit dashboard

## Requirements
- Python 3.x
- Binance Futures Testnet API key and secret

## Setup
1) Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2) Create a local .env file:

```bash
cp .env.example .env
```

3) Edit .env and set your keys (base URL is already testnet):

```
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_secret_here
BINANCE_BASE_URL=https://testnet.binancefuture.com
```

## Run (CLI)
Market order example:

```bash
python main.py market --symbol BTCUSDT --side BUY --quantity 0.001
```

Limit order example:

```bash
python main.py limit --symbol BTCUSDT --side SELL --quantity 0.001 --price 50000
```

The CLI prints:
- Order request summary
- Order response details (orderId, status, executedQty, avgPrice when available)
- Success or failure message

## Logs (Required Deliverable)
All requests, responses, and errors are logged to logs/trades.log. The repository already includes a log file with at least one MARKET and one LIMIT order on the testnet.

## Optional UI
Streamlit dashboard:

```bash
streamlit run streamlit_app.py
```

## Assumptions
- Testnet only (USDT-M). No real funds are used.
- Quantity is rounded to 3 decimal places to avoid precision errors.
- Network failures are reported as a user-facing error.
