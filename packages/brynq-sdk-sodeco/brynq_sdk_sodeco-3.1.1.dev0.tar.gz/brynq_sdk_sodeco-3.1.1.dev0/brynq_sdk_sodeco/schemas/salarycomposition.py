from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime

class SalaryCompositionSchema(DataFrameModel):
    """Schema for salary composition entries"""
    # Required fields
    startdate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Startdate")
    code: int = Field(nullable=False, ge=1, le=8999, alias="Code")

    # Optional fields
    enddate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Enddate")
    days: Optional[int] = Field(nullable=True, ge=0, le=99, alias="Days")
    hours: Optional[float] = Field(nullable=True, ge=0.0, le=9999.0, alias="Hours")
    unity: Optional[float] = Field(nullable=True, alias="Unity")
    percentage: Optional[float] = Field(nullable=True, alias="Percentage")
    amount: Optional[float] = Field(nullable=True, alias="Amount")
    supplement: Optional[float] = Field(nullable=True, alias="Supplement")
    type_of_indexing: Optional[str] = Field(nullable=True, isin=[
        'NoIndexation', 'Indexation', 'FrozenSalary', 'SalaryAboveScale'
    ], alias="TypeOfIndexing")
