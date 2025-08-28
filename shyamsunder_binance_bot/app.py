import os
import time
import threading
from pathlib import Path

import streamlit as st
import pandas as pd

from src.binance_auth import BinanceFuturesREST
from src.orders import market_order, limit_order, stop_limit_order
from src.advanced.twap import twap_market

LOG_FILE = Path(__file__).parent / "bot.log"

st.set_page_config(page_title="Binance Futures Bot (Testnet)", layout="wide")

# --- Session state ---
if "stop_flag" not in st.session_state:
    st.session_state.stop_flag = False
if "last_orders" not in st.session_state:
    st.session_state.last_orders = []

st.title("⚡ Binance Futures Trading Bot — Streamlit UI")
st.caption("Testnet-focused UI to place demo orders and run a TWAP strategy.")

with st.sidebar:
    st.header("🔐 API / Connection")
    api_key = st.text_input("API Key", type="password")
    api_secret = st.text_input("API Secret", type="password")
    testnet = st.toggle("Use Testnet", value=True, help="Recommended for safety")
    timeout = st.number_input("HTTP Timeout (sec)", min_value=5, max_value=60, value=10, step=1)

    st.divider()
    st.header("🧾 Order Parameters")
    symbol = st.text_input("Symbol", value="BTCUSDT", help="Example: BTCUSDT, ETHUSDT")
    side = st.selectbox("Side", ["BUY","SELL"])
    otype = st.selectbox("Order Type", ["MARKET","LIMIT","STOP_LIMIT","TWAP"])
    quantity = st.number_input("Quantity (base asset)", min_value=0.0, value=0.001, step=0.001, format="%.6f")
    tif = st.selectbox("Time in Force", ["GTC","IOC","FOK"], index=0)
    reduce_only = st.checkbox("Reduce Only")

    price = None
    stop_price = None
    slices = None
    interval = None

    if otype in ("LIMIT", "STOP_LIMIT"):
        price = st.number_input("Limit Price", min_value=0.0, value=20000.0, step=1.0, format="%.2f")
    if otype == "STOP_LIMIT":
        stop_price = st.number_input("Stop Trigger Price", min_value=0.0, value=19950.0, step=1.0, format="%.2f")
    if otype == "TWAP":
        slices = st.number_input("Slices", min_value=1, value=5, step=1)
        interval = st.number_input("Interval (seconds)", min_value=1.0, value=2.0, step=1.0)

    st.divider()
    st.header("▶️ Controls")
    start_btn = st.button("Start", type="primary")
    stop_btn = st.button("Stop")
    refresh = st.button("Refresh Balances")

# --- Helpers ---
def require_keys():
    if not api_key or not api_secret:
        st.error("Enter API key and secret in the sidebar to proceed.")
        return False
    return True

def get_client():
    return BinanceFuturesREST(api_key, api_secret, testnet=testnet, timeout=timeout)

def run_order():
    """Executes based on current sidebar selections."""
    client = get_client()
    try:
        if otype == "MARKET":
            status = market_order(client, symbol, side, quantity)
            st.success(f"MARKET order placed")
            st.session_state.last_orders.append(status)
        elif otype == "LIMIT":
            status = limit_order(client, symbol, side, quantity, price, tif=tif, reduce_only=reduce_only)
            st.success("LIMIT order placed")
            st.session_state.last_orders.append(status)
        elif otype == "STOP_LIMIT":
            status = stop_limit_order(client, symbol, side, quantity, limit_price=price, stop_price=stop_price, tif=tif, reduce_only=reduce_only)
            st.success("STOP-LIMIT order placed")
            st.session_state.last_orders.append(status)
        elif otype == "TWAP":
            st.session_state.stop_flag = False
            results = []
            for i in range(int(slices)):
                if st.session_state.stop_flag:
                    st.warning("TWAP stopped by user.")
                    break
                res = market_order(client, symbol, side, float(quantity)/float(slices))
                results.append(res)
                time.sleep(float(interval))
            st.success("TWAP finished")
            st.session_state.last_orders.extend(results)
    except Exception as e:
        st.exception(e)

def tail_log(n=2000):
    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            data = f.read()
        return "\n".join(data.splitlines()[-200:])
    except Exception:
        return "(No log yet)"

# --- Top Metrics ---
cols = st.columns(4)
if require_keys():
    client = get_client()
    st_autorefresh = st.sidebar.toggle("Auto-refresh balances/logs", value=True)
    try:
        code, acct = client.account_info()
        code_b, bals = client.balances()
        wallet = 0.0
        for b in (bals if isinstance(bals, list) else []):
            if b.get("asset") == "USDT":
                wallet = float(b.get("balance", 0.0))
        cols[0].metric("USDT Wallet (est.)", f"{wallet:,.2f}")
        cols[1].metric("Positions", str(len(acct.get("positions", [])) if isinstance(acct, dict) else "-"))
        cols[2].metric("Leverage", next((p.get("leverage") for p in acct.get("positions", []) if p.get("symbol")==symbol), "-") if isinstance(acct, dict) else "-")
        cols[3].metric("Mode", "Testnet" if testnet else "Live")
    except Exception as e:
        cols[0].warning("Balances unavailable (check credentials/Testnet)")

# --- Order form actions ---
if start_btn:
    if require_keys():
        run_order()

if stop_btn:
    st.session_state.stop_flag = True

# --- Recent orders (session only) ---
st.subheader("🧾 Recent Orders (this session)")
if st.session_state.last_orders:
    df = pd.DataFrame(st.session_state.last_orders)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No orders yet.")

# --- Logs ---
st.subheader("📜 Live Logs (tail)")
st.text_area("bot.log tail", tail_log(), height=240, label_visibility="collapsed")

# --- Footer ---
st.caption("⚠️ Educational / Testnet only. Be careful with credentials. No financial advice.")
