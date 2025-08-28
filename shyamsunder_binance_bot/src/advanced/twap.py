import time
from typing import Dict, Any
from ..logger import get_logger
from ..binance_auth import BinanceFuturesREST
from ..orders import market_order

logger = get_logger(__name__)

def twap_market(api: BinanceFuturesREST, symbol: str, side: str, total_qty: float, slices: int, interval_sec: float):
    """Simple TWAP using repeated MARKET orders. Equal slices over total duration.
    NOTE: For demo/testnet only. Production TWAP needs more safeguards.
    """
    if slices <= 0:
        raise ValueError('slices must be > 0')
    qty_per_slice = round(total_qty / slices, 8)
    results = []
    for i in range(slices):
        logger.info(f"TWAP slice {i+1}/{slices} placing {qty_per_slice} {symbol}")
        try:
            res = market_order(api, symbol, side, qty_per_slice)
            results.append(res)
        except Exception as e:
            logger.exception(f"TWAP slice {i+1} failed: {e}")
            results.append({'error': str(e)})
        if i < slices - 1:
            time.sleep(interval_sec)
    return results
