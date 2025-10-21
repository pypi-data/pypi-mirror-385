from __future__ import annotations

import os, time, hmac, hashlib
from typing import Literal, Optional, Dict, Any
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import pandas as pd  # noqa: F401
except Exception:
    pd = None

try:
    import polars as pl  # noqa: F401
except Exception:
    pl = None

from .exceptions import AuthError, APIError

Lib = Literal["pd", "pl"]

DEFAULT_BASE_URL = "https://ohlc.kctradings.com"

class KCClient:
    """Authenticated client for KC Trading OHLC API.

    Defaults:
    - base_url -> https://ohlc.kctradings.com
    - library  -> 'pd' (pandas) at the *call* level if not specified
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        hmac_secret: Optional[str] = None,
        skew_tolerance_s: int = 60,
    ) -> None:
        self.base_url = (base_url or os.getenv("KC_OHLC_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.api_key = api_key or os.getenv("KC_OHLC_API_KEY")
        if not self.api_key:
            raise AuthError("API key missing. Set KC_OHLC_API_KEY or pass api_key.")

        self.timeout = timeout
        self.skew_tolerance_s = skew_tolerance_s
        self.hmac_secret = hmac_secret or os.getenv("KC_OHLC_HMAC_SECRET")

        self.session = requests.Session()
        retry = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    # ---------- Internal helpers ----------

    def _headers(self, method: str, path: str, query: Dict[str, Any]) -> Dict[str, str]:
        headers = {"X-API-KEY": self.api_key}
        if self.hmac_secret:
            ts = str(int(time.time()))
            q = urlencode(sorted((k, str(v)) for k, v in (query or {}).items()))
            payload = f"{method.upper()}\n{path}\n{q}\n{ts}".encode("utf-8")
            sig = hmac.new(self.hmac_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
            headers["X-Timestamp"] = ts
            headers["X-Signature"] = sig
        return headers

    def _handle_response(self, resp: requests.Response) -> Any:
        if 200 <= resp.status_code < 300:
            try:
                return resp.json()
            except ValueError as e:
                raise APIError(f"Invalid JSON response: {e}") from e

        if resp.status_code in (401, 403):
            raise AuthError(f"Unauthorized ({resp.status_code}). Check your API key/signature.")
        raise APIError(f"HTTP {resp.status_code}: {resp.text.strip()}")

    # ---------- Public API ----------

    def get_bars(
        self,
        symbol: str,
        tf: str,
        start: str,
        end: str,
        limit: int = 1_000_000,
        library: Lib = "pd",
    ):
        """Fetch OHLC bars (pandas by default).

        Parameters
        ----------
        library : {'pd','pl'}, default 'pd'
            Dataframe library for this call.
        """
        path = f"/ohlc/range/{symbol}/{tf}"
        url = f"{self.base_url}{path}"
        params = {"start": start, "end": end, "limit": str(limit)}
        headers = self._headers("GET", path, params)
        resp = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
        data = self._handle_response(resp)

        if library == "pl":
            if pl is None:
                raise ImportError("polars not installed. Install with `pip install kc-ohlc[polars]`.")
            df = pl.DataFrame(data)
            if "datetime" in df.columns:
                df = df.with_columns(pl.col("datetime").str.to_datetime(strict=False))
            return df

        if pd is None:
            raise ImportError("pandas not installed. Install with `pip install kc-ohlc[pandas]`.")
        df = pd.DataFrame(data)
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        return df

    def get_symbols(self, library: Lib = "pd"):
        path = "/symbols"
        url = f"{self.base_url}{path}"
        params: Dict[str, Any] = {}
        headers = self._headers("GET", path, params)
        resp = self.session.get(url, headers=headers, timeout=self.timeout)
        data = self._handle_response(resp)

        if library == "pl":
            if pl is None:
                raise ImportError("polars not installed. Install with `pip install kc-ohlc[polars]`.")
            return pl.DataFrame(data)

        if pd is None:
            raise ImportError("pandas not installed. Install with `pip install kc-ohlc[pandas]`.")
        return pd.DataFrame(data)
