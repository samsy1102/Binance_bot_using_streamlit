# Binance Futures Testnet Trading Bot (USDT-M) — CLI

A simplified, **testnet-only** trading bot for Binance USDT-M Futures using **REST calls** (no external SDK required).  
It supports **MARKET**, **LIMIT**, and **STOP-LIMIT** orders, plus an optional **TWAP** convenience strategy.

> Testnet base URL used: `https://testnet.binancefuture.com`

---

## Features
- Place **MARKET** and **LIMIT** orders (required).
- **Buy** and **Sell** sides supported.
- Uses official **Binance Futures REST** endpoints.
- **CLI** input validation and structured **logging** to `bot.log`.
- (Bonus) **STOP-LIMIT** via Futures `STOP` type (uses `stopPrice` + `price`).
- (Bonus) **TWAP** helper that splits a large quantity into timed MARKET slices.

## Quickstart

### 1) Create Testnet account & API keys
- Register and **activate** on Binance Futures **Testnet**.
- Create an **API Key** and **Secret**. **Enable Futures** permission.

### 2) Install dependencies
Python 3.9+ recommended.
```bash
pip install -r requirements.txt
```

> All API interactions are routed to `https://testnet.binancefuture.com` when `--testnet` is set (default).

## Files
```
[project_root]/
├── src/
│   ├── cli.py
│   ├── logger.py
│   ├── binance_auth.py
│   ├── orders.py
│   └── advanced/
│       └── twap.py
├── app.py
└── requirements.txt
```

## Logging
- Logs go to `bot.log` and console.
- Every request/response and error is recorded with timestamps.

## Notes & Gotchas
- **Precision/filters**: Quantities and prices must satisfy the symbol’s lot/price step sizes on Binance Futures. If the API returns a filter error, adjust `quantity`/`price` accordingly.
- **stop-limit** is implemented as Futures `STOP` order: provide both `--stop-price` and `--price` (limit leg).
- For production readiness, add: retries/backoff, exchange info filter checks, and position/risk management.
- If you prefer the official SDK, you can swap `binance_auth.py` for `binance-connector` or `python-binance` Futures methods while keeping the same CLI.

## Requirements
- Python 3.9+
- `requests`

## Security
- **Never** commit your API keys.
- Prefer environment variables or a secure secret manager when running in CI/servers.

## License
MIT


## Streamlit UI

A minimal UI is included at `app.py`.

### Quickstart

```bash
pip install -r requirements.txt
streamlit run app.py
```

Enter your **Binance Testnet** API key/secret in the sidebar, choose a symbol (e.g., `BTCUSDT`), pick an order type (MARKET/LIMIT/STOP_LIMIT or TWAP), then click **Start**.

> ⚠️ This UI is for **educational/testnet** use. Double‑check credentials and symbols.
