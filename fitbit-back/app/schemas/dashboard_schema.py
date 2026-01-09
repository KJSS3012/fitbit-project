from pydantic import BaseModel
from typing import List

# -----------------------------------
# RESPONSE MODELS (OUTPUT)
# -----------------------------------

# Chart axes (Frontend receives ready-to-use arrays)
class ChartData(BaseModel):
    dates: List[str]
    steps: List[int]
    bpm: List[float]
    sleep: List[float]

# Summary cards (Averages displayed at the top of the screen)
class DashboardSummary(BaseModel):
    avg_steps: int
    avg_bpm: int
    avg_sleep: float
    days_analyzed: int

# The main object returned by the API
class DashboardResponse(BaseModel):
    period: str
    summary: DashboardSummary
    charts: ChartData