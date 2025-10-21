from __future__ import annotations

import os, argparse
from .client import KCClient

def main():
    parser = argparse.ArgumentParser(prog="kc-ohlc", description="CLI for KC OHLC API")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sym = sub.add_parser("symbols", help="List available symbols")
    p_sym.add_argument("--lib", choices=["pd", "pl"], default="pd")

    p_bars = sub.add_parser("bars", help="Fetch OHLC bars")
    p_bars.add_argument("symbol")
    p_bars.add_argument("tf", help="timeframe, e.g. m1, m5, h1, d1")
    p_bars.add_argument("--start", required=True)
    p_bars.add_argument("--end", required=True)
    p_bars.add_argument("--limit", type=int, default=1_000_000)
    p_bars.add_argument("--lib", choices=["pd", "pl"], default="pd")

    args = parser.parse_args()

    client = KCClient(
        base_url=os.getenv("KC_OHLC_BASE_URL"),  # falls back to embedded default
        api_key=os.getenv("KC_OHLC_API_KEY"),
        # hmac_secret via env if desired
    )

    if args.cmd == "symbols":
        df = client.get_symbols(library=args.lib)
        if args.lib == "pd":
            print(df.to_csv(index=False))
        else:
            print(df.write_csv())
        return

    if args.cmd == "bars":
        df = client.get_bars(args.symbol, args.tf, start=args.start, end=args.end, limit=args.limit, library=args.lib)
        if args.lib == "pd":
            print(df.to_csv(index=False))
        else:
            print(df.write_csv())

if __name__ == "__main__":
    main()
