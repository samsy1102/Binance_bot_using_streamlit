import time
import hmac
import hashlib
from urllib.parse import urlencode
import requests
from typing import Dict, Any, Optional, Tuple

DEFAULT_RECV_WINDOW = 5000

class BinanceFuturesREST:
    """Minimal REST client for Binance USDT-M Futures (Testnet by default)."""
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True, timeout: int = 10):
        self.api_key = api_key
        self.api_secret = api_secret.encode('utf-8')
        self.timeout = timeout
        # Testnet base URL provided in the assignment
        self.base_url = 'https://testnet.binancefuture.com' if testnet else 'https://fapi.binance.com'
        self._session = requests.Session()
        self._session.headers.update({'X-MBX-APIKEY': api_key})

    # --- Helpers ---
    def _sign(self, params: Dict[str, Any]) -> str:
        query = urlencode(params, doseq=True)
        return hmac.new(self.api_secret, query.encode('utf-8'), hashlib.sha256).hexdigest()

    def _send(self, method: str, path: str, params: Dict[str, Any], signed: bool = False) -> Tuple[int, Dict[str, Any]]:
        url = self.base_url + path
        if signed:
            params = dict(params)  # copy
            params['timestamp'] = int(time.time() * 1000)
            if 'recvWindow' not in params:
                params['recvWindow'] = DEFAULT_RECV_WINDOW
            params['signature'] = self._sign(params)
        if method.upper() in ('GET', 'DELETE'):
            resp = self._session.request(method.upper(), url, params=params, timeout=self.timeout)
        else:
            resp = self._session.request(method.upper(), url, data=params, timeout=self.timeout)
        try:
            data = resp.json()
        except Exception:
            data = {'raw': resp.text}
        return resp.status_code, data

    # --- Public endpoints ---
    def ping(self):
        return self._send('GET', '/fapi/v1/ping', {}, signed=False)

    def server_time(self):
        return self._send('GET', '/fapi/v1/time', {}, signed=False)

    # --- Private endpoints ---
    def place_order(self, **kwargs):
        """POST /fapi/v1/order (SIGNED). Accepts standard Binance Futures order params."""
        return self._send('POST', '/fapi/v1/order', kwargs, signed=True)

    def query_order(self, symbol: str, orderId: Optional[int] = None, origClientOrderId: Optional[str] = None):
        params = {'symbol': symbol}
        if orderId is not None:
            params['orderId'] = orderId
        if origClientOrderId is not None:
            params['origClientOrderId'] = origClientOrderId
        return self._send('GET', '/fapi/v1/order', params, signed=True)

    def cancel_order(self, symbol: str, orderId: Optional[int] = None, origClientOrderId: Optional[str] = None):
        params = {'symbol': symbol}
        if orderId is not None:
            params['orderId'] = orderId
        if origClientOrderId is not None:
            params['origClientOrderId'] = origClientOrderId
        return self._send('DELETE', '/fapi/v1/order', params, signed=True)

    # --- Added convenience getters ---
    def account_info(self):
        """GET /fapi/v2/account (signed)"""
        return self._send('GET', '/fapi/v2/account', signed=True)

    def balances(self):
        """GET /fapi/v2/balance (signed)"""
        return self._send('GET', '/fapi/v2/balance', signed=True)

    def position_risk(self, symbol: str = None):
        """GET /fapi/v2/positionRisk (signed). If symbol is provided, filter on client side."""
        status, data = self._send('GET', '/fapi/v2/positionRisk', signed=True)
        if symbol and isinstance(data, list):
            data = [p for p in data if p.get('symbol') == symbol]
        return status, data

    def income_history(self, symbol: str = None, incomeType: str = None, limit: int = 50):
        """GET /fapi/v1/income (signed)"""
        params = {}
        if symbol: params['symbol'] = symbol
        if incomeType: params['incomeType'] = incomeType
        params['limit'] = limit
        return self._send('GET', '/fapi/v1/income', params, signed=True)

