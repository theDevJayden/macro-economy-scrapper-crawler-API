from pydantic import BaseModel
from typing import Optional, List

class MacroIndicatorResponse(BaseModel):
    status: str
    country: str
    indicator_name: str
    series_id: str
    latest_value: float
    unit: str
    observation_date: str
    trend_summary: Optional[str] = None

class CommodityResponse(BaseModel):
    status: str
    symbol: str
    name: str
    current_price: float
    currency: str
    change_percent: float
    last_updated: str