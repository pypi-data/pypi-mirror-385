from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional, Sequence, Union

from fin68.exceptions import DataDecodingError

from .http_core import HttpSession
from .helpers import Interval
from .progress import start_progress,update_progress,finish_progress
ENDPOINT = "/market-data/eod/ohlcv"


def _normalize_symbols(symbols: Union[str, Sequence[str]]) -> List[str]:
    """Return a normalised, non-empty list of uppercase symbols."""
    if isinstance(symbols, str):
        cleaned = symbols.strip()
        if not cleaned:
            raise ValueError("symbol must not be empty.")
        return [cleaned.upper()]

    if not isinstance(symbols, Sequence) or isinstance(symbols, bytes):
        raise TypeError("symbol must be a string or a sequence of strings.")

    normalised: List[str] = []
    symbols=list(set(symbols))
    for item in symbols:
        if not isinstance(item, str):
            raise TypeError("All symbols in the sequence must be strings.")
        cleaned = item.strip()
        if not cleaned:
            continue
        normalised.append(cleaned.upper())

    if not normalised:
        raise ValueError("symbol sequence must contain at least one non-empty string.")
    return normalised


def _render_progress(current: int, total: int, symbol: str) -> None:
    """Render a progress bar"""
    if total <= 0:
        return

    bar_width = 49
    progress = current / total
    filled = int(bar_width * progress)
    bar = "*" * filled + " " * (bar_width - filled)
    percent = int(progress * 100)
    message = f"[{bar}] {percent:3d}%  {current} of {total} completed | {symbol}"

    sys.stdout.write("\r" + message)
    sys.stdout.flush()
    if current == total:
        sys.stdout.write("\n")
        sys.stdout.flush()


def fetch_ohlcv(
    session: HttpSession,
    symbol: Union[str, Sequence[str]],
    start: Optional[str] = None,
    end: Optional[str] = None,
    interval: Interval = "1D",
    adjusted: Optional[bool] = None,
    *,
    show_progress: bool = True,
) -> List[Dict[str, Any]]:
    """Fetch raw OHLCV data for one or multiple symbols."""

    symbols = _normalize_symbols(symbol)
    total = len(symbols)

    all_rows: List[Dict[str, Any]] = []
    start_progress(total, "Batch EOD")
    for index, current_symbol in enumerate(symbols, start=1):
        params: Dict[str, Any] = {"symbol": current_symbol, "interval": interval}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if adjusted is not None:
            params["adjusted"] = "true" if adjusted else "false"

        response = session.get(ENDPOINT, params=params)

        try:
            payload = response.json()
        except ValueError as exc:
            raise DataDecodingError("Unable to decode OHLCV response as JSON") from exc

        if not isinstance(payload, dict):
            raise DataDecodingError("Unexpected payload structure for OHLCV response.")

        if payload.get("error"):
            raise DataDecodingError(f"Backend returned error for {current_symbol}: {payload['error']}")

        data = payload.get("data")
        if not isinstance(data, list):
            raise DataDecodingError("Unexpected payload format for OHLCV series.")

        account_type = payload.get("account_type")

        for item in data:
            result={}
            result['symbol']=current_symbol
            if not isinstance(item, dict):
                raise DataDecodingError("Each OHLCV row must be a dictionary.")
            # Ensure symbol metadata is present for downstream consumers.
            result.update(item)
            # if account_type is not None and "account_type" not in item:
            #     item["account_type"] = account_type
            all_rows.append(result)
        if show_progress :
            update_progress(index)
            # _render_progress(index, total, current_symbol)
    finish_progress()
    return all_rows
