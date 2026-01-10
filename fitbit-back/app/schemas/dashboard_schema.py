from pydantic import BaseModel, Field
from typing import List, Dict

# -----------------------------------
# RESPONSE MODELS (OUTPUT)
# -----------------------------------

class HeartRateValue(BaseModel):
    restingHeartRate: int

class HeartRateRecord(BaseModel):
    dateTime: str
    value: HeartRateValue

class StepRecord(BaseModel):
    dateTime: str
    value: str

class SleepRecord(BaseModel):
    dateOfSleep: str
    minutesAsleep: int

class DashboardResponse(BaseModel):
    activities_steps: List[StepRecord] = Field(..., alias="activities-steps")
    activities_heart: List[HeartRateRecord] = Field(..., alias="activities-heart")
    sleep: List[SleepRecord]

    class Config:
        populate_by_name = True
        serialization_alias_kind = "alias"