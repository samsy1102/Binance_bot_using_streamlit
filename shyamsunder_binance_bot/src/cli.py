import argparse
import json
from typing import Any
from .logger import get_logger
from .binance_auth import BinanceFuturesREST
from .orders import market_order, limit_order, stop_limit_order
from .advanced.twap import twap_market

logger = get_logger('cli')

def main():
    parser = argparse.ArgumentParser(description='Binance Futures Testnet Trading Bot (USDT-M)')
    parser.add_argument('--api-key', required=True, help='Binance API key')
    parser.add_argument('--api-secret', required=True, help='Binance API secret')
    parser.add_argument('--symbol', required=True, help='Trading symbol, e.g., BTCUSDT')
    parser.add_argument('--side', required=True, choices=['BUY','SELL'])
    parser.add_argument('--type', required=True, help='Order type: MARKET, LIMIT, STOP_LIMIT, or TWAP')
    parser.add_argument('--quantity', type=float, required=False, help='Order quantity (base asset)')
    parser.add_argument('--price', type=float, help='Limit price (for LIMIT) or limit leg (for STOP_LIMIT)')
    parser.add_argument('--stop-price', type=float, help='Stop trigger price (for STOP_LIMIT)')
    parser.add_argument('--tif', default='GTC', help='Time in force: GTC/IOC/FOK')
    parser.add_argument('--reduce-only', action='store_true', help='Set reduceOnly=true')
    parser.add_argument('--testnet', action='store_true', default=True, help='Use Testnet (default True)')
    # TWAP specific
    parser.add_argument('--slices', type=int, help='TWAP: number of slices')
    parser.add_argument('--interval', type=float, help='TWAP: seconds between slices')

    args = parser.parse_args()
    api = BinanceFuturesREST(args.api_key, args.api_secret, testnet=args.testnet)

    try:
        if args.type.upper() == 'MARKET':
            if args.quantity is None:
                raise ValueError('quantity is required for MARKET')
            data = market_order(api, args.symbol, args.side, args.quantity, reduce_only=args.reduce_only)

        elif args.type.upper() == 'LIMIT':
            if args.quantity is None or args.price is None:
                raise ValueError('quantity and price are required for LIMIT')
            data = limit_order(api, args.symbol, args.side, args.quantity, args.price, tif=args.tif, reduce_only=args.reduce_only)

        elif args.type.upper() == 'STOP_LIMIT':
            if args.quantity is None or args.price is None or args.stop_price is None:
                raise ValueError('quantity, price, and stop-price are required for STOP_LIMIT')
            data = stop_limit_order(api, args.symbol, args.side, args.quantity, args.stop_price, args.price, tif=args.tif, reduce_only=args.reduce_only)

        elif args.type.upper() == 'TWAP':
            if args.quantity is None or args.slices is None or args.interval is None:
                raise ValueError('quantity, slices, and interval are required for TWAP')
            data = twap_market(api, args.symbol, args.side, args.quantity, args.slices, args.interval)
        else:
            raise ValueError('Unsupported type. Use MARKET, LIMIT, STOP_LIMIT, or TWAP')

        print(json.dumps({'ok': True, 'result': data}, indent=2))
        logger.info(f"Order result: {data}")

    except Exception as e:
        logger.exception(f"Error: {e}")
        print(json.dumps({'ok': False, 'error': str(e)}))

if __name__ == '__main__':
    main()
