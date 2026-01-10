from pydantic import BaseModel, Field, ConfigDict
from typing import List

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
    # Standard Fitbit aliases
    activities_steps: List[StepRecord] = Field(..., alias="activities-steps")
    activities_heart: List[HeartRateRecord] = Field(..., alias="activities-heart")
    sleep: List[SleepRecord]

    # Pydantic V2 modern configuration
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )