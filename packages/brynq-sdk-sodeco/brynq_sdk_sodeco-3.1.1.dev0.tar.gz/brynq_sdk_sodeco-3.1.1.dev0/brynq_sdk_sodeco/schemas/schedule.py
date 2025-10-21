from pandera import DataFrameModel, Field, Column
from typing import Optional, List
import pandas as pd

class ScheduleWeekSchema(DataFrameModel):
    """Schema for schedule week entries"""
    week_number: int = Field(nullable=False, ge=1, le=15, alias='WeekNumber')
    day_1: Optional[float] = Field(nullable=True, ge=0.0, le=24.0, alias="Day1")
    day_2: Optional[float] = Field(nullable=True, ge=0.0, le=24.0, alias="Day2")
    day_3: Optional[float] = Field(nullable=True, ge=0.0, le=24.0, alias="Day3")
    day_4: Optional[float] = Field(nullable=True, ge=0.0, le=24.0, alias="Day4")
    day_5: Optional[float] = Field(nullable=True, ge=0.0, le=24.0, alias="Day5")
    day_6: Optional[float] = Field(nullable=True, ge=0.0, le=24.0, alias="Day6")
    day_7: Optional[float] = Field(nullable=True, ge=0.0, le=24.0, alias="Day7")

    class Config:
        strict = True
        coerce = True

class ScheduleSchema(DataFrameModel):
    """Schema for schedule entries"""
    schedule_id: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 4}, alias="ScheduleID")
    description: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 50}, alias="Description")
    start_date: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="StartDate")
    week: List[dict] = Field(nullable=False, alias="Week")  # List of ScheduleWeek objects

    class Config:
        strict = True
        coerce = True

    @classmethod
    def validate_weeks(cls, weeks: List[dict]) -> bool:
        """Validate a list of schedule weeks against the ScheduleWeekSchema"""
        if not weeks:
            return False

        try:
            df = pd.DataFrame(weeks)
            ScheduleWeekSchema.validate(df)
            return True
        except Exception:
            return False
