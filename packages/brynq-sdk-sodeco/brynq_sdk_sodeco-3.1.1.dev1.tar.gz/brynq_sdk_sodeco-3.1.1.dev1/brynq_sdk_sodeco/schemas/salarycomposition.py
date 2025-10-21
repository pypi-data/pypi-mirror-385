from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class SalaryCompositionGet(BrynQPanderaDataFrameModel):
    """Schema for validating SalaryCompositions extracted from Contract data."""

    # Required
    start_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Start date in YYYYMMDD format", alias="Startdate")
    code: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Salary composition code", alias="Code", ge=1, le=8999)

    # Optional fields
    end_date: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="End date in YYYYMMDD format", alias="Enddate")
    days: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Days", alias="Days", ge=0, le=9999)
    hours: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Hours", alias="Hours", ge=0.0, le=9999.0)
    unity: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Unity", alias="Unity")
    percentage: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Percentage", alias="Percentage")
    amount: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Amount", alias="Amount")
    supplement: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Supplement", alias="Supplement")
    type_of_indexing: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Type of indexing", alias="TypeOfIndexing")
    contract_startdate: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Contract start date for identification", alias="contract_startdate")
    worker_number: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Worker number for identification", alias="worker_number")
    contract_identifier: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Derived identifier workerNumber_startdate", alias="contract_identifier")
    worker_number: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Worker number", alias="WorkerNumber")


    class _Annotation:
        primary_key = None
        # Foreign keys/identifiers added by processing layer
