# backend/tools/finance_data.py

import httpx
from datetime import date
from typing import Dict, Any, Optional

from ..utils.cache import cache_get, cache_set


# ------------------------------
# CONFIG / CONSTANTS
# ------------------------------

# Example public API (AlphaVantage or others may require API keys)
FALLBACK_NAV = 100.0  # Default NAV if APIs fail


# ------------------------------
# Helper: Build Unified Output
# ------------------------------
def _build_output(symbol: str, date_str: str, nav: float,
                  fund_type: str = "unknown", risk_level: str = "unknown") -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "date": date_str,
        "nav": float(nav),
        "fund_type": fund_type,
        "risk_level": risk_level
    }


# ------------------------------
# Main Function: NAV Fetch
# ------------------------------
def fetch_nav_data(symbol: str, date_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches NAV data for a mutual fund / stock.
    Uses caching to reduce network dependency.
    Returns a clean dict for NAVResponse model.
    """

    if not date_str:
        date_str = date.today().isoformat()

    # -----------------------------------
    # Step 1: Check Cache
    # -----------------------------------
    cache_key = f"NAV:{symbol}:{date_str}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    # -----------------------------------
    # Step 2: Try External API (exchangerate.host style)
    # Replace this with MF API or stock API if needed.
    # -----------------------------------
    try:
        # Dummy API hit (replace with real MF API)
        # For example: https://api.mfapi.in/mf/<fund_code>
        # Or AlphaVantage TIME_SERIES_DAILY
        url = "https://api.exchangerate.host/latest"  # Just a harmless free API for demo

        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url)
            resp.raise_for_status()

        # Fake NAV computation for demo:
        # In real world: parse actual NAV or stock price
        nav_value = float(hash(symbol) % 100) + 50.0  # Semi-random deterministic

        result = _build_output(
            symbol=symbol,
            date_str=date_str,
            nav=nav_value,
            fund_type="equity_large_cap",
            risk_level="high"
        )

        # Save to cache
        cache_set(cache_key, result)
        return result

    except Exception:
        # -----------------------------------
        # Step 3: Fallback NAV
        # -----------------------------------
        fallback = _build_output(
            symbol=symbol,
            date_str=date_str,
            nav=FALLBACK_NAV,
            fund_type="unknown",
            risk_level="unknown"
        )
        cache_set(cache_key, fallback)
        return fallback
