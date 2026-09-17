import os
import requests
import yfinance as yf
from dotenv import load_dotenv
from app.schemas.macro_schema import MacroIndicatorResponse, CommodityResponse

# Load environment variables from .env file
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY", "")

# Mapping friendly indicator keys to official FRED Series IDs
SERIES_MAP = {
    "cpi": "CPIAUCSL",          # Consumer Price Index (Inflation benchmark)
    "unemployment": "UNRATE",   # Unemployment / Jobless Rate
    "fed_rate": "FEDFUNDS"      # Federal Reserve Interest Rate
}

# Mapping friendly commodity keys to Yahoo Finance Tickers
COMMODITY_MAP = {
    "gold": {"ticker": "GC=F", "name": "Gold Futures"},
    "oil": {"ticker": "CL=F", "name": "Crude Oil WTI"},
    "coal": {"ticker": "BTU", "name": "Global Coal Benchmark (Peabody Proxy)"},
    "nickel": {"ticker": "VALE", "name": "Global Nickel Market Benchmark (Vale Proxy)"}
}


def fetch_us_macro_indicator(indicator_key: str) -> MacroIndicatorResponse:
    """Fetches macro statistics (CPI, Unemployment, Interest Rates) from FRED."""
    indicator_key = indicator_key.lower()
    if indicator_key not in SERIES_MAP:
        raise ValueError(f"Invalid indicator key. Choose from: {list(SERIES_MAP.keys())}")
    
    series_id = SERIES_MAP[indicator_key]
    
    # Graceful fallback if FRED_API_KEY is not set yet in .env
    if not FRED_API_KEY:
        return MacroIndicatorResponse(
            status="error_no_api_key",
            country="USA",
            indicator_name=indicator_key.upper(),
            series_id=series_id,
            latest_value=0.0,
            unit="N/A",
            observation_date="N/A",
            trend_summary="Please provide FRED_API_KEY in .env file."
        )

    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
    response = requests.get(url, timeout=10.0)
    
    if response.status_code != 200:
        return MacroIndicatorResponse(
            status="error_fetching",
            country="USA",
            indicator_name=indicator_key.upper(),
            series_id=series_id,
            latest_value=0.0,
            unit="N/A",
            observation_date="N/A"
        )

    data = response.json()
    # Exclude missing observations marked as "." by FRED
    observations = [obs for obs in data.get("observations", []) if obs.get("value") != "."]
    
    if not observations:
        return MacroIndicatorResponse(
            status="no_data",
            country="USA",
            indicator_name=indicator_key.upper(),
            series_id=series_id,
            latest_value=0.0,
            unit="N/A",
            observation_date="N/A"
        )

    # Get the latest data point released
    latest = observations[-1]
    
    return MacroIndicatorResponse(
        status="success",
        country="USA",
        indicator_name=indicator_key.upper(),
        series_id=series_id,
        latest_value=float(latest["value"]),
        unit="Index/Percent",
        observation_date=latest["date"]
    )


def fetch_commodity_price(commodity_key: str) -> CommodityResponse:
    """Scrapes market price & 24h performance for commodities from Yahoo Finance."""
    commodity_key = commodity_key.lower()
    if commodity_key not in COMMODITY_MAP:
        raise ValueError(f"Invalid commodity key. Choose from: {list(COMMODITY_MAP.keys())}")
        
    info = COMMODITY_MAP[commodity_key]
    ticker = yf.Ticker(info["ticker"])
    history = ticker.history(period="2d")
    
    if history.empty:
        return CommodityResponse(
            status="error_no_data",
            symbol=info["ticker"],
            name=info["name"],
            current_price=0.0,
            currency="USD",
            change_percent=0.0,
            last_updated="N/A"
        )
        
    latest_price = float(history["Close"].iloc[-1])
    prev_price = float(history["Close"].iloc[0]) if len(history) > 1 else latest_price
    
    # Calculate daily percentage movement
    pct_change = 0.0
    if prev_price > 0:
        pct_change = round(((latest_price - prev_price) / prev_price) * 100, 2)
    
    return CommodityResponse(
        status="success",
        symbol=info["ticker"],
        name=info["name"],
        current_price=round(latest_price, 2),
        currency="USD",
        change_percent=pct_change,
        last_updated=str(history.index[-1].date())
    )