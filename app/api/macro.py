from fastapi import APIRouter, HTTPException, Query
from app.schemas.macro_schema import MacroIndicatorResponse, CommodityResponse
from app.services.macro_fetcher import fetch_us_macro_indicator, fetch_commodity_price

# APIRouter allows us to group related endpoints under a clean prefix
router = APIRouter(
    prefix="/api/v1/macro",
    tags=["Macroeconomic & Commodity Intelligence"]
)

@router.get("/indicator", response_model=MacroIndicatorResponse)
def get_macro_indicator(
    name: str = Query(..., description="Indicator key: 'cpi', 'unemployment', or 'fed_rate'")
):
    """
    Fetches US macroeconomic metrics (CPI, Unemployment, Fed Rate) from FRED.
    Used primarily by the Macro Strategist AI Agent.
    """
    try:
        data = fetch_us_macro_indicator(name)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/commodity", response_model=CommodityResponse)
def get_commodity_price(
    name: str = Query(..., description="Commodity key: 'gold', 'oil', 'coal', or 'nickel'")
):
    """
    Scrapes live price and 24h change for global commodities (Gold, Oil, Coal, Nickel).
    Used by Fundamental Investor and Commodity AI Agents.
    """
    try:
        data = fetch_commodity_price(name)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")