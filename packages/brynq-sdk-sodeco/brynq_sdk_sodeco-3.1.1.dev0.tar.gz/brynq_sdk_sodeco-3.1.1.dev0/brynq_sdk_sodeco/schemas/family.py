from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime

class FamilySchema(DataFrameModel):
    # Required fields
    startdate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Startdate")

    # Optional fields (CivilStatus is now optional according to the latest schema)
    civil_status: Optional[str] = Field(nullable=True, isin=[
        'Single', 'Married', 'Widow', 'Divorced', 'Separated',
        'Cohabitation', 'LiveTogether'
    ], alias="CivilStatus")
    enddate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Enddate")
    worker_handicapped: Optional[str] = Field(nullable=True, isin=['N', 'Y'], alias="WorkerHandicapped")
    worker_single_with_children: Optional[str] = Field(nullable=True, isin=['N', 'Y'], alias="WorkerSingleWithChildren")
    spouse_with_income: Optional[str] = Field(nullable=True, isin=[
        'WithIncome', 'WithoutIncome', 'ProffIncomeLessThan235',
        'ProffIncomeLessThan141', 'ProffIncomeLessThan469'
    ], alias="SpouseWithIncome")
    spouse_handicapped: Optional[str] = Field(nullable=True, isin=['N', 'Y'], alias="SpouseHandicapped")
    spouse_name: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 40}, alias="SpouseName")
    spouse_firstname: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 25}, alias="SpouseFirstname")
    spouse_inss: Optional[float] = Field(nullable=True, ge=0, le=99999999999.0, alias="SpouseINSS")
    spouse_sex: Optional[str] = Field(nullable=True, isin=['M', 'F'], alias="SpouseSex")
    spouse_profession: Optional[str] = Field(nullable=True, isin=[
        'Handworker', 'Servant', 'Employee', 'SelfEmployed', 'Miner',
        'Sailor', 'CivilServant', 'Other', 'Nil'
    ], alias="SpouseProfession")
    spouse_birthdate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="SpouseBirthdate")
    spouse_birthplace: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30}, alias="SpouseBirthplace")

    # Integer fields with min/max values
    children_at_charge: Optional[int] = Field(nullable=True, ge=0, le=99, alias="ChildrenAtCharge")
    children_handicapped: Optional[int] = Field(nullable=True, ge=0, le=99, alias="ChildrenHandicapped")
    others_at_charge: Optional[int] = Field(nullable=True, ge=0, le=99, alias="OthersAtCharge")
    others_handicapped: Optional[int] = Field(nullable=True, ge=0, le=99, alias="OthersHandicapped")
    others_65_at_charge: Optional[int] = Field(nullable=True, ge=0, le=99, alias="Others65AtCharge")
    # Added missing field from the latest schema
    wage_garnishment_children_at_charge: Optional[int] = Field(nullable=True, ge=0, le=99, alias="WageGarnishmentChildrenAtCharge")
    others_65_handicapped: Optional[int] = Field(nullable=True, ge=0, le=99, alias="Others65Handicapped")
    others_65_need_of_care: Optional[int] = Field(nullable=True, ge=0, le=99, alias="Others65NeedOfCare")
    child_benefit_institution: Optional[int] = Field(nullable=True, ge=0, le=9999, alias="ChildBenefitInstitution")

    # Additional optional fields
    child_benefit_reference: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 15}, alias="ChildBenefitReference")
    weddingdate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', alias="Weddingdate")
