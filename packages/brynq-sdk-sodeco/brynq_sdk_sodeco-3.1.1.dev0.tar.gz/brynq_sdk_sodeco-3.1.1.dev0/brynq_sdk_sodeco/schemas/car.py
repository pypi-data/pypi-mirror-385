from pandera import Field
from typing import Optional
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class CarSchema(BrynQPanderaDataFrameModel):
    """Schema for company car entries"""
    # Required fields
    starting_date: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="StartingDate")
    license_plate: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 15}, alias="LicensePlate")

    # Optional fields
    ending_date: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="EndingDate")
    worker_id: Optional[int] = Field(nullable=True, alias="WorkerId")
    cat_rsz: Optional[str] = Field(nullable=True, str_length={'min_value': 3, 'max_value': 3}, regex=r'^[0-9]*$', alias="CatRSZ")
    motor_type: Optional[str] = Field(nullable=True, isin=['Gasoline', 'Diesel', 'LPG', 'Electric', 'CNG'], alias="MotorType")
    tax_horsepower: Optional[int] = Field(nullable=True, ge=0, le=99, alias="TaxHorsepower")
    co2_emissions_hybride_wltp: Optional[int] = Field(nullable=True, ge=0, le=500, alias="Co2EmissionsHybrideWLTP")
    co2_emissions_hybride: Optional[int] = Field(nullable=True, ge=0, le=500, alias="Co2EmissionsHybride")
    co2_emissions_wltp: Optional[int] = Field(nullable=True, ge=0, le=500, alias="Co2EmissionsWLTP")
    co2_emissions: Optional[int] = Field(nullable=True, ge=0, le=500, alias="Co2Emissions")
    code: Optional[int] = Field(nullable=True, ge=4000, le=8999, alias="Code")
    fuel_card: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 20}, alias="FuelCard")
    brand: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 50})
    order_date: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="OrderDate")
    registration_date: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="RegistrationDate")
    catalog_price: Optional[float] = Field(nullable=True, alias="CatalogPrice")
    light_truck: Optional[str] = Field(nullable=True, isin=['N', 'Y'], alias="LightTruck")
    informative: Optional[str] = Field(nullable=True, isin=['N', 'Y'], alias="Informative")
    pool_car: Optional[str] = Field(nullable=True, isin=['N', 'Y'], alias="PoolCar")
    pers_contribution_amount: Optional[float] = Field(nullable=True, alias="PersContributionAmount")
    pers_contribution_percentage: Optional[float] = Field(nullable=True, alias="PersContributionPercentage")
    pers_contribution_code: Optional[int] = Field(nullable=True, ge=4000, le=8999, alias="PersContributionCode")

    class Config:
        strict = True
        coerce = True
