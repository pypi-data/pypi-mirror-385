# kc-ohlc (v0.2.1)

Changes:
- **Embedded default base URL**: `https://ohlc.kctradings.com` (no need to pass `base_url`).
- **Per-call library override**: `get_bars(..., library="pd")` / `get_symbols(..., library="pd")`, default is **pandas**.

## Quickstart
```python
from kc_ohlc import KCClient

c = KCClient(api_key="YOUR_KEY")       # base_url defaults internally
df = c.get_bars("EURUSD", "h1", "2024-01-01", "2025-01-01")            # pandas by default
df_pl = c.get_bars("EURUSD", "h1", "2024-01-01", "2025-01-01", library="pl")  # per-call polars
```

CLI still works with env vars; default base URL embedded.
