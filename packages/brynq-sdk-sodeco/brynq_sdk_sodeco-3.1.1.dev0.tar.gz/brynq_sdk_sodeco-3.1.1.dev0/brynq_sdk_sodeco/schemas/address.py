from pandera import Field
from typing import Optional
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class AddressSchema(BrynQPanderaDataFrameModel):
    # Required fields
    startdate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Startdate")
    street: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 100}, alias="Street")
    house_number: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 10}, alias="HouseNumber")
    zip_code: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 12}, alias="ZIPCode")
    city: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 30}, alias="City")
    country: str = Field(nullable=False, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default='00150', alias="Country")

    # Optional fields
    enddate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Enddate")
    post_box: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 5}, alias="PostBox")
    distance: Optional[float] = Field(nullable=True, ge=0.0, le=99999.9, alias="Distance")
