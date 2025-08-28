from typing import Optional, Dict, Any
from .binance_auth import BinanceFuturesREST
from .logger import get_logger

logger = get_logger(__name__)

VALID_SIDES = {'BUY', 'SELL'}
VALID_TYPES = {'MARKET', 'LIMIT', 'STOP', 'TAKE_PROFIT'}
# We'll expose STOP_LIMIT as a friendly alias that maps to Binance 'STOP' (with price + stopPrice)
FRIENDLY_TYPES = {'MARKET', 'LIMIT', 'STOP_LIMIT'}

def _validate_common(symbol: str, side: str, quantity: float):
    if not symbol or not symbol.isalnum():
        raise ValueError('Invalid symbol. Example: BTCUSDT')
    if side.upper() not in VALID_SIDES:
        raise ValueError("Invalid side. Use one of: BUY, SELL")
    if quantity <= 0:
        raise ValueError('Quantity must be positive.')

def market_order(api: BinanceFuturesREST, symbol: str, side: str, quantity: float, reduce_only: bool=False) -> Dict[str, Any]:
    _validate_common(symbol, side, quantity)
    params = {
        'symbol': symbol.upper(),
        'side': side.upper(),
        'type': 'MARKET',
        'quantity': quantity,
        'reduceOnly': 'true' if reduce_only else 'false',
    }
    logger.info(f"Placing MARKET order: {params}")
    status, data = api.place_order(**params)
    logger.info(f"Response ({status}): {data}")
    if status != 200:
        raise RuntimeError(f"Order failed: {data}")
    return data

def limit_order(api: BinanceFuturesREST, symbol: str, side: str, quantity: float, price: float, tif: str='GTC', reduce_only: bool=False) -> Dict[str, Any]:
    _validate_common(symbol, side, quantity)
    if price <= 0:
        raise ValueError('Price must be positive for LIMIT orders.')
    if tif not in {'GTC','IOC','FOK'}:
        raise ValueError('timeInForce must be one of GTC, IOC, FOK.')
    params = {
        'symbol': symbol.upper(),
        'side': side.upper(),
        'type': 'LIMIT',
        'quantity': quantity,
        'price': price,
        'timeInForce': tif,
        'reduceOnly': 'true' if reduce_only else 'false',
    }
    logger.info(f"Placing LIMIT order: {params}")
    status, data = api.place_order(**params)
    logger.info(f"Response ({status}): {data}")
    if status != 200:
        raise RuntimeError(f"Order failed: {data}")
    return data

def stop_limit_order(api: BinanceFuturesREST, symbol: str, side: str, quantity: float, stop_price: float, limit_price: float, tif: str='GTC', reduce_only: bool=False) -> Dict[str, Any]:
    """Implements a STOP-LIMIT using Binance Futures 'STOP' type which takes both stopPrice and price."""
    _validate_common(symbol, side, quantity)
    if stop_price <= 0 or limit_price <= 0:
        raise ValueError('stop_price and limit_price must be positive.')
    if tif not in {'GTC','IOC','FOK'}:
        raise ValueError('timeInForce must be one of GTC, IOC, FOK.')
    params = {
        'symbol': symbol.upper(),
        'side': side.upper(),
        'type': 'STOP',
        'quantity': quantity,
        'stopPrice': stop_price,
        'price': limit_price,
        'timeInForce': tif,
        'reduceOnly': 'true' if reduce_only else 'false',
        # 'workingType': 'CONTRACT_PRICE',  # Optional: or 'MARK_PRICE'
    }
    logger.info(f"Placing STOP-LIMIT order: {params}")
    status, data = api.place_order(**params)
    logger.info(f"Response ({status}): {data}")
    if status != 200:
        raise RuntimeError(f"Order failed: {data}")
    return data
