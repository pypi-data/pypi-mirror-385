from pandera import Field as PanderaField
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from enum import Enum
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# ============================================================================
# GET SCHEMAS (Pandera - for DataFrame validation)
# ============================================================================

class EmployeeGet(BrynQPanderaDataFrameModel):
    """Pandera schema for validating employee/worker data retrieved from Sodeco API. This schema is used to validate the main worker DataFrame returned by Workers.get()"""

    # Required fields
    worker_number: int = PanderaField(nullable=False, ge=1, le=9999999, description="Unique worker identifier", alias="WorkerNumber")
    name: str = PanderaField(nullable=False, str_length={'min_value': 0, 'max_value': 40}, description="Worker last name", alias="Name")
    first_name: str = PanderaField(nullable=False, str_length={'min_value': 0, 'max_value': 25}, description="Worker first name", alias="Firstname")
    employer: str = PanderaField(nullable=False, description="Employer identifier", alias="employer")

    # Optional personal information fields
    initial: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 1}, description="Worker initial", alias="Initial")
    inss: Optional[float] = PanderaField(nullable=True, ge=0.0, le=99999999999.0, description="National Insurance (INSS) number", alias="INSS")
    sex: Optional[str] = PanderaField(nullable=True, isin=['M', 'F'], description="Worker gender (M/F)", alias="Sex")
    birth_date: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Birth date in YYYYMMDD format", alias="Birthdate")
    birth_place_zip_code: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 12}, description="Birthplace ZIP code", alias="BirthplaceZIPCode")
    birth_place: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 30}, description="Birthplace city name", alias="Birthplace")
    birth_place_country: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', description="Birthplace country code (5 digits)", alias="BirthplaceCountry")
    nationality: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', description="Nationality country code (5 digits)", alias="Nationality")
    language: Optional[str] = PanderaField(nullable=True, isin=['N', 'F', 'D', 'E'], description="Primary language (N=Dutch, F=French, D=German, E=English)", alias="Language")

    # Payment information
    pay_way: Optional[str] = PanderaField(nullable=True, isin=['Cash', 'Transfer', 'Electronic', 'AssignmentList'], description="Payment method", alias="PayWay")
    pay_model: Optional[str] = PanderaField(nullable=True, isin=['Monthly', 'Weekly', 'Daily', 'Hourly'], description="Payment frequency model", alias="PayModel")
    bank_account: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 45}, description="Bank account number (IBAN)", alias="BankAccount")
    bic_code: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15}, description="Bank BIC/SWIFT code", alias="BICCode")

    # Identification documents
    id: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15}, description="Identity document number", alias="ID")
    id_type: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 3}, description="Type of identity document", alias="IDType")
    id_valid_until: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="ID document expiration date in YYYYMMDD format", alias="IDValidUntil")
    driver_license: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15}, description="Driver license number", alias="DriverLicense")
    driver_category: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 2}, description="Driver license category", alias="DriverCategory")

    # Vehicle and transport
    number_plate: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Vehicle license plate number", alias="NumberPlate")
    fuel_card: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 20}, description="Fuel card number", alias="FuelCard")
    travel_expenses: Optional[str] = PanderaField(nullable=True, isin=['PublicTransportTrain', 'OwnTransport', 'PublicTransportOther', 'Bicycle', 'None'], description="Type of travel expenses", alias="TravelExpenses")
    type_of_travel_expenses: Optional[str] = PanderaField(nullable=True, isin=['Other', 'PublicCommonTransport', 'OrganisedCommonTransport'], description="Category of travel expenses", alias="TypeOfTravelExpenses")
    salary_code_travel_expenses: Optional[int] = PanderaField(nullable=True, ge=0, le=9999, description="Salary code for travel expenses (0 = none)", alias="SalaryCodeTravelExpenses")

    # Professional information
    education: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 20}, description="Education level", alias="Education")
    profession: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 50}, description="Worker profession/job title", alias="Profession")

    # Insurance information
    e_health_insurance: Optional[int] = PanderaField(nullable=True, ge=0, le=9999, description="E-health insurance institution code", alias="EHealthInsurance")
    e_health_insurance_reference: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 20}, description="E-health insurance reference number", alias="EHealthInsuranceReference")
    accident_insurance: Optional[int] = PanderaField(nullable=True, ge=0, le=9999, description="Accident insurance institution code", alias="AccidentInsurance")
    medical_center: Optional[int] = PanderaField(nullable=True, ge=0, le=9999, description="Medical center institution code", alias="MedicalCenter")
    medical_center_reference: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15}, description="Medical center reference number", alias="MedicalCenterReference")

    # Additional fields
    external_id: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 50}, description="External system identifier", alias="ExternalID")
    interim_from: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Interim work start date in YYYYMMDD format", alias="InterimFrom")
    interim_to: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Interim work end date in YYYYMMDD format", alias="InterimTo")
    expat: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Worker is expatriate (Y/N)", alias="Expat")
    main_division: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Main division code", alias="MainDivision")

    class Config:
        strict = True
        coerce = True


class FamilyGet(BrynQPanderaDataFrameModel):
    """Pandera schema for validating family status data retrieved from Sodeco API."""

    # Required fields
    worker_number: int = PanderaField(nullable=False, ge=1, le=9999999, description="Worker number reference", alias="WorkerNumber")
    start_date: str = PanderaField(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Family status start date in YYYYMMDD format", alias="Startdate")

    # Optional fields
    end_date: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Family status end date in YYYYMMDD format", alias="Enddate")
    civil_status: Optional[str] = PanderaField(nullable=True, isin=['Single', 'Married', 'Widow', 'Divorced', 'Separated', 'Cohabitation', 'LiveTogether'], description="Civil/marital status", alias="CivilStatus")
    worker_handicapped: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Worker has handicap (Y/N)", alias="WorkerHandicapped")
    worker_single_with_children: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Worker is single parent (Y/N)", alias="WorkerSingleWithChildren")

    # Spouse information
    spouse_with_income: Optional[str] = PanderaField(nullable=True, isin=['WithIncome', 'WithoutIncome', 'ProffIncomeLessThan235', 'ProffIncomeLessThan141', 'ProffIncomeLessThan469'], description="Spouse income status", alias="SpouseWithIncome")
    spouse_handicapped: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Spouse has handicap (Y/N)", alias="SpouseHandicapped")
    spouse_name: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 40}, description="Spouse last name", alias="SpouseName")
    spouse_first_name: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 25}, description="Spouse first name", alias="SpouseFirstname")
    spouse_inss: Optional[float] = PanderaField(nullable=True, ge=0, le=99999999999.0, description="Spouse national insurance number", alias="SpouseINSS")
    spouse_sex: Optional[str] = PanderaField(nullable=True, isin=['M', 'F'], description="Spouse gender (M/F)", alias="SpouseSex")
    spouse_profession: Optional[str] = PanderaField(nullable=True, isin=['Handworker', 'Servant', 'Employee', 'SelfEmployed', 'Miner', 'Sailor', 'CivilServant', 'Other', 'Nil'], description="Spouse profession category", alias="SpouseProfession")
    spouse_birth_date: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Spouse birth date in YYYYMMDD format", alias="SpouseBirthdate")
    spouse_birth_place: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 30}, description="Spouse birthplace", alias="SpouseBirthplace")

    # Dependents information
    children_at_charge: Optional[int] = PanderaField(nullable=True, ge=0, le=99, description="Number of children at charge", alias="ChildrenAtCharge")
    children_handicapped: Optional[int] = PanderaField(nullable=True, ge=0, le=99, description="Number of handicapped children", alias="ChildrenHandicapped")
    others_at_charge: Optional[int] = PanderaField(nullable=True, ge=0, le=99, description="Number of other dependents", alias="OthersAtCharge")
    others_handicapped: Optional[int] = PanderaField(nullable=True, ge=0, le=99, description="Number of other handicapped dependents", alias="OthersHandicapped")
    others_65_at_charge: Optional[int] = PanderaField(nullable=True, ge=0, le=99, description="Number of dependents over 65", alias="Others65AtCharge")
    wage_garnishment_children_at_charge: Optional[int] = PanderaField(nullable=True, ge=0, le=99, description="Number of children for wage garnishment", alias="WageGarnishmentChildrenAtCharge")
    others_65_handicapped: Optional[int] = PanderaField(nullable=True, ge=0, le=99, description="Number of handicapped dependents over 65", alias="Others65Handicapped")
    others_65_need_of_care: Optional[int] = PanderaField(nullable=True, ge=0, le=99, description="Number of dependents over 65 needing care", alias="Others65NeedOfCare")

    # Child benefit information
    child_benefit_institution: Optional[int] = PanderaField(nullable=True, ge=0, le=9999, description="Child benefit institution code", alias="ChildBenefitInstitution")
    child_benefit_reference: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15}, description="Child benefit reference number", alias="ChildBenefitReference")
    wedding_date: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Wedding date in YYYYMMDD format", alias="Weddingdate")

    class Config:
        strict = True
        coerce = True


class AddressGet(BrynQPanderaDataFrameModel):
    """Pandera schema for validating address data retrieved from Sodeco API."""

    # Required fields
    worker_number: int = PanderaField(nullable=False, ge=1, le=9999999, description="Worker number reference", alias="WorkerNumber")
    start_date: str = PanderaField(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Address valid from date in YYYYMMDD format", alias="Startdate")
    street: str = PanderaField(nullable=False, str_length={'min_value': 0, 'max_value': 100}, description="Street name", alias="Street")
    house_number: str = PanderaField(nullable=False, str_length={'min_value': 0, 'max_value': 10}, description="House number", alias="HouseNumber")
    zip_code: str = PanderaField(nullable=False, str_length={'min_value': 0, 'max_value': 12}, description="Postal/ZIP code", alias="ZIPCode")
    city: str = PanderaField(nullable=False, str_length={'min_value': 0, 'max_value': 30}, description="City name", alias="City")
    country: str = PanderaField(nullable=False, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', description="Country code (5 digits, default 00150 for Belgium)", alias="Country")

    # Optional fields
    end_date: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Address valid until date in YYYYMMDD format", alias="Enddate")
    post_box: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 5}, description="Post office box number", alias="PostBox")
    distance: Optional[float] = PanderaField(nullable=True, ge=0.0, le=99999.9, description="Distance from workplace in kilometers", alias="Distance")

    class Config:
        strict = True
        coerce = True


class CommunicationGet(BrynQPanderaDataFrameModel):
    """Pandera schema for validating communication/contact data retrieved from Sodeco API."""

    # Required fields
    worker_number: int = PanderaField(nullable=False, ge=1, le=9999999, description="Worker number reference", alias="WorkerNumber")
    communication_type: str = PanderaField(nullable=False, isin=['None', 'Phone', 'GSM', 'Email', 'PrivatePhone', 'Fax', 'InternalPhone', 'PrivateEmail', 'GSMEntreprise', 'Website'], description="Type of communication method", alias="CommunicationType")
    value: str = PanderaField(nullable=False, str_length={'min_value': 0, 'max_value': 100}, description="Communication value (phone number, email address, etc.)", alias="Value")

    # Optional fields
    id: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 100}, description="Communication entry identifier", alias="ID")
    contact_person: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 100}, description="Contact person last name", alias="ContactPerson")
    contact_person_first_name: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 50}, description="Contact person first name", alias="ContactPersonFirstname")

    class Config:
        strict = True
        coerce = True


class ContractGet(BrynQPanderaDataFrameModel):
    """Pandera schema for validating contract data retrieved from Sodeco API."""

    # Required fields
    worker_number: int = PanderaField(nullable=False, ge=1, le=9999999, description="Worker number reference", alias="WorkerNumber")
    start_date: str = PanderaField(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Contract start date in YYYYMMDD format", alias="Startdate")

    # Optional fields - contract basic info
    end_date: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Contract end date in YYYYMMDD format", alias="Enddate")
    employment_status: Optional[str] = PanderaField(nullable=True, isin=['Workman', 'Employee', 'Director'], description="Employment status type", alias="EmploymentStatus")
    contract: Optional[str] = PanderaField(nullable=True, description="Contract type code", alias="Contract")

    # Social security
    cat_rsz: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 3}, regex=r'^[0-9]*$', description="Social security category code", alias="CatRSZ")
    par_com: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Parity committee code", alias="ParCom")
    document_c78: Optional[str] = PanderaField(nullable=True, description="Document C78 status", alias="DocumentC78")
    code_c98: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Code C98 flag", alias="CodeC98")
    code_c131a: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Code C131A flag", alias="CodeC131A")
    code_c131a_request_ft: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Code C131A request full-time flag", alias="CodeC131ARequestFT")
    code_c131: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Code C131 flag", alias="CodeC131")
    risk: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Risk code", alias="Risk")
    social_security_card: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 20}, description="Social security card number", alias="SocialSecurityCard")
    work_permit: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 20}, description="Work permit number", alias="WorkPermit")

    # Working time
    working_time: Optional[str] = PanderaField(nullable=True, isin=['Fulltime', 'PartTime'], description="Working time type (full-time/part-time)", alias="WorkingTime")
    spec_working_time: Optional[str] = PanderaField(nullable=True, isin=['Regular', 'Interruptions', 'SeasonalWorker'], description="Special working time specification", alias="SpecWorkingTime")
    schedule: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 4}, description="Schedule code", alias="Schedule")
    weekhours_worker: Optional[float] = PanderaField(nullable=True, ge=0, le=200, description="Weekly work hours for worker", alias="WeekhoursWorker")
    weekhours_employer: Optional[float] = PanderaField(nullable=True, ge=0, le=200, description="Weekly work hours for employer calculation", alias="WeekhoursEmployer")
    weekhours_worker_average: Optional[float] = PanderaField(nullable=True, ge=0, le=200, description="Average weekly work hours for worker", alias="WeekhoursWorkerAverage")
    weekhours_employer_average: Optional[float] = PanderaField(nullable=True, ge=0, le=200, description="Average weekly work hours for employer", alias="WeekhoursEmployerAverage")
    weekhours_worker_effective: Optional[float] = PanderaField(nullable=True, ge=0, le=200, description="Effective weekly work hours for worker", alias="WeekhoursWorkerEffective")
    weekhours_employer_effective: Optional[float] = PanderaField(nullable=True, ge=0, le=200, description="Effective weekly work hours for employer", alias="WeekhoursEmployerEffective")
    days_week: Optional[float] = PanderaField(nullable=True, ge=0, le=7, description="Number of work days per week", alias="DaysWeek")
    days_week_ft: Optional[float] = PanderaField(nullable=True, ge=0, le=7, description="Full-time equivalent days per week", alias="DaysWeekFT")
    reducing_working_kind: Optional[str] = PanderaField(nullable=True, description="Type of working time reduction", alias="ReducingWorkingKind")
    reducing_working_kind_days: Optional[float] = PanderaField(nullable=True, ge=0, le=365, description="Days of working time reduction", alias="ReducingWorkingKindDays")
    reducing_working_kind_hours: Optional[float] = PanderaField(nullable=True, ge=0, le=9999, description="Hours of working time reduction", alias="ReducingWorkingKindHours")
    part_time_return_towork: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Part-time return to work code", alias="PartTimeReturnTowork")
    asr_schedule: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="ASR schedule code", alias="ASRSchedule")

    # Professional information
    proff_cat: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Professional category code", alias="ProffCat")
    function: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Function code", alias="Function")
    function_description: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 100}, description="Function description text", alias="FunctionDescription")
    social_balance_joblevel: Optional[str] = PanderaField(nullable=True, description="Social balance job level category", alias="SocialBalanceJoblevel")

    # Organizational
    office: Optional[int] = PanderaField(nullable=True, ge=0, le=9999, description="Office code", alias="Office")
    division: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Division code", alias="Division")
    invoicing_division: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Invoicing division code", alias="InvoicingDivision")
    cost_centre: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15}, description="Cost center code", alias="CostCentre")

    # Dates
    date_in_service: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Date when worker entered service in YYYYMMDD format", alias="DateInService")
    date_out_service: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Date when worker left service in YYYYMMDD format", alias="DateOutService")
    reason_out: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Reason for leaving service", alias="ReasonOut")
    seniority: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Seniority date in YYYYMMDD format", alias="Seniority")
    sector_seniority: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Sector seniority date in YYYYMMDD format", alias="SectorSeniority")
    date_professional_experience: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Professional experience start date in YYYYMMDD format", alias="DateProfessionalExperience")
    scale_salary_seniority: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Scale salary seniority date in YYYYMMDD format", alias="ScaleSalarySeniority")

    # Probation and fixed term
    start_probation_period: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Probation period start date in YYYYMMDD format", alias="StartProbationPeriod")
    end_probation_period: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Probation period end date in YYYYMMDD format", alias="EndProbationPeriod")
    fixed_term: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Fixed-term contract flag", alias="FixedTerm")
    end_fixed_term: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Fixed-term contract end date in YYYYMMDD format", alias="EndFixedTerm")

    # Scale salary
    scale_salary_prisma: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Scale salary Prisma flag", alias="ScaleSalaryPrisma")
    scale_salary_use: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Use scale salary flag", alias="ScaleSalaryUse")
    scale_salary_definition: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Scale salary definition code", alias="ScaleSalaryDefinition")
    scale_salary_category: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Scale salary category", alias="ScaleSalaryCategory")
    scale_salary_scale: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Scale salary scale", alias="ScaleSalaryScale")

    # Other
    security: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Security code", alias="Security")
    substitute_contract: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Substitute contract flag", alias="SubstituteContract")

    # Student information (nested)
    student_exist: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Student contract exists", alias="Student.Exist")
    student_solidarity_contribution: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Student solidarity contribution", alias="Student.SolidarityContribution")

    # Career break (nested)
    career_break_exist: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Career break exists", alias="CareerBreak.Exist")
    career_break_kind: Optional[str] = PanderaField(nullable=True, description="Career break kind", alias="CareerBreak.Kind")
    career_break_reason: Optional[str] = PanderaField(nullable=True, description="Career break reason", alias="CareerBreak.Reason")
    career_break_originally_contract_type: Optional[str] = PanderaField(nullable=True, description="Original contract type before career break", alias="CareerBreak.OriginallyContractType")
    career_break_weekhours_worker_before: Optional[float] = PanderaField(nullable=True, ge=0, le=200, description="Worker hours before career break", alias="CareerBreak.WeekhoursWorkerBefore")
    career_break_weekhours_employer_before: Optional[float] = PanderaField(nullable=True, ge=0, le=200, description="Employer hours before career break", alias="CareerBreak.WeekhoursEmployerBefore")

    # International employment (nested)
    international_employment_exist: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="International employment exists", alias="InternationalEmployment.Exist")
    international_employment_kind: Optional[str] = PanderaField(nullable=True, description="International employment kind", alias="InternationalEmployment.Kind")
    international_employment_border_country: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10}, description="Border country code for international employment", alias="InternationalEmployment.BorderCountry")

    # Progressive work resumption (nested)
    progressive_work_resumption_exist: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Progressive work resumption exists", alias="ProgressiveWorkResumption.Exist")
    progressive_work_resumption_risk: Optional[str] = PanderaField(nullable=True, description="Progressive work resumption risk type", alias="ProgressiveWorkResumption.Risk")
    progressive_work_resumption_hours: Optional[float] = PanderaField(nullable=True, ge=0, le=200, description="Progressive work resumption hours per week", alias="ProgressiveWorkResumption.Hours")
    progressive_work_resumption_minutes: Optional[float] = PanderaField(nullable=True, ge=0, le=59, description="Progressive work resumption additional minutes", alias="ProgressiveWorkResumption.Minutes")
    progressive_work_resumption_days: Optional[float] = PanderaField(nullable=True, ge=0, le=7, description="Progressive work resumption days per week", alias="ProgressiveWorkResumption.Days")
    progressive_work_resumption_startdate_illness: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Progressive work resumption illness start date in YYYYMMDD format", alias="ProgressiveWorkResumption.StartdateIllness")
    progressive_work_resumption_comment: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 250}, description="Progressive work resumption comment", alias="ProgressiveWorkResumption.Comment")

    class Config:
        strict = True
        coerce = True


class TaxGet(BrynQPanderaDataFrameModel):
    """Pandera schema for validating tax data retrieved from Sodeco API."""

    # Required fields
    worker_number: int = PanderaField(nullable=False, ge=1, le=9999999, description="Worker number reference", alias="WorkerNumber")
    start_date: str = PanderaField(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Tax configuration start date in YYYYMMDD format", alias="Startdate")
    tax_calculation: str = PanderaField(nullable=False, isin=['Normal', 'ConversionPT', 'FiscVolAmount', 'FiscVolPercent', 'Amount', 'Percent', 'PercentNormal', 'NonResident', 'NoCity', 'NoTax', 'Younger', 'NormalPlus', 'Trainer', 'NormalMinPerc', 'NormalMinAmount'], description="Tax calculation method", alias="TaxCalculation")

    # Optional fields
    value: Optional[float] = PanderaField(nullable=True, ge=0.0, le=9999999999.0, description="Tax value (amount or percentage depending on calculation type)", alias="Value")
    flexi_retired: Optional[str] = PanderaField(nullable=True, isin=['N', 'Y'], description="Flexi-retired worker flag", alias="FlexiRetired")

    class Config:
        strict = True
        coerce = True


class ReplacementGet(BrynQPanderaDataFrameModel):
    """Pandera schema for validating replacement worker data retrieved from Sodeco API."""

    # Required fields
    worker_number: int = PanderaField(nullable=False, ge=1, le=9999999, description="Worker number being replaced", alias="WorkerNumber")
    replacement_worker_number: int = PanderaField(nullable=False, ge=1, le=9999999, description="Replacement worker number", alias="ReplacementWorkerNumber")
    start_date: str = PanderaField(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Replacement start date in YYYYMMDD format", alias="Startdate")

    # Optional fields
    end_date: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Replacement end date in YYYYMMDD format", alias="Enddate")
    percentage: Optional[float] = PanderaField(nullable=True, ge=0.0, le=100.0, description="Replacement percentage", alias="Percentage")

    class Config:
        strict = True
        coerce = True


class SalaryCompositionGet(BrynQPanderaDataFrameModel):
    """Pandera schema for validating salary composition data retrieved from Sodeco API."""

    # Required fields
    worker_number: int = PanderaField(nullable=False, ge=1, le=9999999, description="Worker number reference", alias="WorkerNumber")
    start_date: str = PanderaField(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Salary composition start date in YYYYMMDD format", alias="Startdate")
    code: int = PanderaField(nullable=False, ge=1, le=8999, description="Salary composition code", alias="Code")

    # Optional fields
    end_date: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$', description="Salary composition end date in YYYYMMDD format", alias="Enddate")
    days: Optional[int] = PanderaField(nullable=True, ge=0, le=99, description="Number of days", alias="Days")
    hours: Optional[float] = PanderaField(nullable=True, ge=0, le=9999, description="Number of hours", alias="Hours")
    unity: Optional[float] = PanderaField(nullable=True, description="Unity value", alias="Unity")
    percentage: Optional[float] = PanderaField(nullable=True, description="Percentage value", alias="Percentage")
    amount: Optional[float] = PanderaField(nullable=True, description="Amount value", alias="Amount")
    supplement: Optional[float] = PanderaField(nullable=True, description="Supplement amount", alias="Supplement")
    type_of_indexing: Optional[str] = PanderaField(nullable=True, isin=['NoIndexation', 'Indexation', 'FrozenSalary', 'SalaryAboveScale'], description="Type of salary indexing", alias="TypeOfIndexing")

    class Config:
        strict = True
        coerce = True


# ============================================================================
# POST/PUT SCHEMAS (Pydantic - for request validation)
# ============================================================================


class ExistEnum(str, Enum):
    NO = 'N'
    YES = 'Y'


class CareerBreakKindEnum(str, Enum):
    FULLTIME = 'Fulltime'
    PART_TIME_ONE_FIFTH = 'PartTimeOneFifth'
    PART_TIME_ONE_QUARTER = 'PartTimeOneQuarter'
    PART_TIME_ONE_THIRD = 'PartTimeOneThird'
    PART_TIME_HALF = 'PartTimeHalf'
    PART_TIME_THREE_FIFTHS = 'PartTimeThreeFifths'
    PART_TIME_ONE_TENTH = 'PartTimeOneTenth'


class CareerBreakReasonEnum(str, Enum):
    PALLIATIVE_CARE = 'PalliativeCare'
    SERIOUSLY_ILL = 'SeriouslyIll'
    OTHER = 'Other'
    PARENTAL_LEAVE = 'ParentalLeave'
    CRISIS = 'Crisis'
    FAMILY_CARE = 'FamilyCare'
    END_OF_CAREER = 'EndOfCareer'
    SICK_CHILD = 'SickChild'
    FAMILY_CARE_CORONA = 'FamilyCareCorona'
    CHILD_CARE_UNDER_8 = 'ChildCareUnder8'
    CHILD_CARE_HANDICAP_UNDER_21 = 'ChildCareHandicapUnder21'
    CERTIFIED_TRAINING = 'CertifiedTraining'


class ContractTypeEnum(str, Enum):
    FULLTIME = 'Fulltime'
    PART_TIME = 'PartTime'


class CivilStatusEnum(str, Enum):
    SINGLE = 'Single'
    MARRIED = 'Married'
    WIDOW = 'Widow'
    DIVORCED = 'Divorced'
    SEPARATED = 'Separated'
    COHABITATION = 'Cohabitation'
    LIVE_TOGETHER = 'LiveTogether'


class SpouseIncomeEnum(str, Enum):
    WITH_INCOME = 'WithIncome'
    WITHOUT_INCOME = 'WithoutIncome'
    PROFF_INCOME_LESS_THAN_235 = 'ProffIncomeLessThan235'
    PROFF_INCOME_LESS_THAN_141 = 'ProffIncomeLessThan141'
    PROFF_INCOME_LESS_THAN_469 = 'ProffIncomeLessThan469'


class SpouseProfessionEnum(str, Enum):
    HANDWORKER = 'Handworker'
    SERVANT = 'Servant'
    EMPLOYEE = 'Employee'
    SELF_EMPLOYED = 'SelfEmployed'
    MINER = 'Miner'
    SAILOR = 'Sailor'
    CIVIL_SERVANT = 'CivilServant'
    OTHER = 'Other'
    NIL = 'Nil'


class TaxCalculationEnum(str, Enum):
    NORMAL = 'Normal'
    CONVERSION_PT = 'ConversionPT'
    FISC_VOL_AMOUNT = 'FiscVolAmount'
    FISC_VOL_PERCENT = 'FiscVolPercent'
    AMOUNT = 'Amount'
    PERCENT = 'Percent'
    PERCENT_NORMAL = 'PercentNormal'
    NON_RESIDENT = 'NonResident'
    NO_CITY = 'NoCity'
    NO_TAX = 'NoTax'
    YOUNGER = 'Younger'
    NORMAL_PLUS = 'NormalPlus'
    TRAINER = 'Trainer'
    NORMAL_MIN_PERC = 'NormalMinPerc'
    NORMAL_MIN_AMOUNT = 'NormalMinAmount'


class CareerBreakDefinition(BaseModel):
    exist: ExistEnum = Field(..., alias="Exist")
    kind: Optional[CareerBreakKindEnum] = Field(None, alias="Kind")
    reason: Optional[CareerBreakReasonEnum] = Field(None, alias="Reason")
    originally_contract_type: Optional[ContractTypeEnum] = Field(None, alias="OriginallyContractType")
    weekhours_worker_before: Optional[float] = Field(None, alias="WeekhoursWorkerBefore")
    weekhours_employer_before: Optional[float] = Field(None, alias="WeekhoursEmployerBefore")

    class Config:
        populate_by_name = True


class CertainWorkDefinition(BaseModel):
    exist: ExistEnum = Field(..., alias="Exist")
    description: Optional[str] = Field(None, min_length=0, max_length=250, alias="Description")

    class Config:
        populate_by_name = True


class Address(BaseModel):
    start_date: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    end_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Enddate")
    street: str = Field(..., min_length=0, max_length=100, alias="Street")
    house_number: str = Field(..., min_length=0, max_length=10, alias="HouseNumber")
    post_box: Optional[str] = Field(None, min_length=0, max_length=5, alias="PostBox")
    zip_code: str = Field(..., min_length=0, max_length=12, alias="ZIPCode")
    city: str = Field(..., min_length=0, max_length=30, alias="City")
    country: str = Field(default='00150', min_length=5, max_length=5, pattern=r'^[0-9]*$', alias="Country")
    distance: Optional[float] = Field(None, ge=0.0, le=99999.9, alias="Distance")

    class Config:
        populate_by_name = True


class Communication(BaseModel):
    communication_type: Literal['None', 'Phone', 'GSM', 'Email', 'PrivatePhone', 'Fax', 'InternalPhone', 'PrivateEmail', 'GSMEntreprise', 'Website'] = Field(..., alias="CommunicationType")
    value: str = Field(..., min_length=0, max_length=100, alias="Value")
    contact_person: Optional[str] = Field(None, min_length=0, max_length=100, alias="ContactPerson")

    class Config:
        populate_by_name = True


EmploymentStatusType = Literal['Workman', 'Employee', 'Director']
ContractLiteral = Literal['Usually', 'FlexiVerbal', 'FlexiWritten', 'FlexiLiable', 'Sportsperson', 'Housekeeper', 'Servant', 'Agriculture', 'Homework', 'HomeworkChildcare', 'Physician', 'PhysicianTraining', 'PhysicianIndependant', 'ApprenticeFlemisch', 'ApprenticeFrench', 'ApprenticeGerman', 'ApprenticeManager', 'ApprenticeIndustrial', 'ApprenticeSocio', 'ApprenticeBio', 'ApprenticeAlternating', 'EarlyRetirement', 'EarlyRetirementPartTime', 'FreeNOSS', 'FreeNOSSManager', 'FreeNOSSOther', 'FreeNOSSSportingEvent', 'FreeNOSSHelper', 'FreeNOSSSocio', 'FreeNOSSEducation', 'FreeNOSSSpecialCultures', 'FreeNOSSVolunteer', 'Horeca', 'HorecaExtraHourLiable', 'HorecaExtraDayLiable', 'HorecaExtraHourForfait', 'HorecaExtraDayForfait', 'HorecaFlexiVerbal', 'HorecaFlexiWritten', 'HorecaFlexiLiable', 'Construction', 'ConstructionAlternating', 'ConstructionApprenticeYounger', 'ConstructionApprentice', 'ConstructionGodfather', 'JobTrainingIBO', 'JobTrainingSchool', 'JobTrainingVDAB', 'JobTrainingLiberalProfession', 'JobTrainingEntry', 'JobTrainingPFIWa', 'JobTrainingABO', 'JobTrainingPFIBx', 'JobTrainingBIO', 'JobTrainingAlternating', 'JobTrainingDisability', 'NonProfitRiziv', 'NonProfitGesco', 'NonProfitDAC', 'NonProfitPrime', 'NonProfitLowSkilled', 'Artist', 'ArtistWithContract', 'ArtistWithoutContract', 'Transport', 'TransportNonMobile', 'TransportGarage', 'Aircrew', 'AircrewPilot', 'AircrewCabinCrew', 'Interim', 'InterimTemporary', 'InterimsPermanent', 'External', 'ExternalApplicant', 'ExternalSubcontractor', 'ExternalAgentIndependant', 'ExternalExtern', 'ExternalIntern', 'ExternalLegalPerson', 'SalesRepresentative', 'SportsTrainer']


class Contract(BaseModel):
    start_date: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    end_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Enddate")
    employment_status: Optional[EmploymentStatusType] = Field(None, alias="EmploymentStatus")
    contract: Optional[ContractLiteral] = Field(None, alias="Contract")
    career_break: Optional[CareerBreakDefinition] = Field(None, alias="CareerBreak")
    certain_work: Optional[CertainWorkDefinition] = Field(None, alias="CertainWork")

    class Config:
        populate_by_name = True


class FamilyStatus(BaseModel):
    start_date: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    end_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Enddate")
    civil_status: Optional[CivilStatusEnum] = Field(None, alias="CivilStatus")
    worker_handicapped: Optional[ExistEnum] = Field(None, alias="WorkerHandicapped")
    worker_single_with_children: Optional[ExistEnum] = Field(None, alias="WorkerSingleWithChildren")
    spouse_with_income: Optional[SpouseIncomeEnum] = Field(None, alias="SpouseWithIncome")
    spouse_handicapped: Optional[ExistEnum] = Field(None, alias="SpouseHandicapped")
    spouse_name: Optional[str] = Field(None, min_length=0, max_length=40, alias="SpouseName")
    spouse_first_name: Optional[str] = Field(None, min_length=0, max_length=25, alias="SpouseFirstname")
    spouse_inss: Optional[float] = Field(None, ge=0.0, le=99999999999.0, alias="SpouseINSS")
    spouse_sex: Optional[Literal['M', 'F']] = Field(None, alias="SpouseSex")
    spouse_birth_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="SpouseBirthdate")
    spouse_profession: Optional[SpouseProfessionEnum] = Field(None, alias="SpouseProfession")
    spouse_birth_place: Optional[str] = Field(None, min_length=0, max_length=30, alias="SpouseBirthplace")
    children_at_charge: Optional[int] = Field(None, ge=0, le=99, alias="ChildrenAtCharge")
    children_handicapped: Optional[int] = Field(None, ge=0, le=99, alias="ChildrenHandicapped")
    others_at_charge: Optional[int] = Field(None, ge=0, le=99, alias="OthersAtCharge")
    others_handicapped: Optional[int] = Field(None, ge=0, le=99, alias="OthersHandicapped")
    others_65_at_charge: Optional[int] = Field(None, ge=0, le=99, alias="Others65AtCharge")
    others_65_handicapped: Optional[int] = Field(None, ge=0, le=99, alias="Others65Handicapped")
    child_benefit_institution: Optional[int] = Field(None, ge=0, le=9999, alias="ChildBenefitInstitution")
    child_benefit_reference: Optional[str] = Field(None, min_length=0, max_length=15, alias="ChildBenefitReference")
    wedding_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="WeddingDate")

    class Config:
        populate_by_name = True


class Tax(BaseModel):
    start_date: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    tax_calculation: TaxCalculationEnum = Field(..., alias="TaxCalculation")
    value: Optional[float] = Field(None, ge=0.0, le=9999999999.0, alias="Value")

    class Config:
        populate_by_name = True


class Replacement(BaseModel):
    worker_number: int = Field(..., ge=1, le=9999999, alias="WorkerNumber")
    start_date: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    end_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Enddate")
    percentage: Optional[float] = Field(None, ge=0.0, le=100.0, alias="Percentage")

    class Config:
        populate_by_name = True


class WorkerCreate(BaseModel):
    """Pydantic schema for creating/updating worker data in Sodeco API. Used for POST and PUT operations."""

    # Required fields
    worker_number: int = Field(..., ge=1, le=9999999, alias="WorkerNumber")
    name: str = Field(..., min_length=0, max_length=40, alias="Name")
    first_name: str = Field(..., min_length=0, max_length=25, alias="Firstname")

    # Optional basic fields
    initial: Optional[str] = Field(None, min_length=1, max_length=1, alias="Initial")
    inss: Optional[float] = Field(None, ge=0.0, le=99999999999.0, alias="INSS")
    sex: Optional[Literal['M', 'F']] = Field(None, alias="Sex")
    birth_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Birthdate")
    birth_place_zip_code: Optional[str] = Field(None, min_length=0, max_length=12, alias="BirthplaceZIPCode")
    birth_place: Optional[str] = Field(None, min_length=0, max_length=30, alias="Birthplace")
    birth_place_country: Optional[str] = Field(default='00150', min_length=5, max_length=5, pattern=r'^[0-9]*$', alias="BirthplaceCountry")
    nationality: Optional[str] = Field(default='00150', min_length=5, max_length=5, pattern=r'^[0-9]*$', alias="Nationality")
    language: Optional[Literal['N', 'F', 'D', 'E']] = Field(None, alias="Language")
    pay_way: Optional[Literal['Cash', 'Transfer', 'Electronic', 'AssignmentList']] = Field(None, alias="PayWay")
    bank_account: Optional[str] = Field(None, min_length=0, max_length=45, alias="BankAccount")
    bic_code: Optional[str] = Field(None, min_length=0, max_length=15, alias="BICCode")
    id: Optional[str] = Field(None, min_length=0, max_length=15, alias="ID")
    id_type: Optional[str] = Field(None, min_length=0, max_length=3, alias="IDType")
    id_valid_until: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="IDValidUntil")
    driver_license: Optional[str] = Field(None, min_length=0, max_length=15, alias="DriverLicense")
    driver_category: Optional[str] = Field(None, min_length=0, max_length=2, alias="DriverCategory")
    number_plate: Optional[str] = Field(None, min_length=0, max_length=10, alias="NumberPlate")
    fuel_card: Optional[str] = Field(None, min_length=0, max_length=20, alias="FuelCard")
    education: Optional[str] = Field(None, min_length=0, max_length=20, alias="Education")
    profession: Optional[str] = Field(None, min_length=0, max_length=50, alias="Profession")
    e_health_insurance: Optional[int] = Field(None, ge=0, le=9999, alias="EHealthInsurance")
    e_health_insurance_reference: Optional[str] = Field(None, min_length=0, max_length=20, alias="EHealthInsuranceReference")
    accident_insurance: Optional[int] = Field(None, ge=0, le=9999, alias="AccidentInsurance")
    medical_center: Optional[int] = Field(None, ge=0, le=9999, alias="MedicalCenter")
    medical_center_reference: Optional[str] = Field(None, min_length=0, max_length=15, alias="MedicalCenterReference")
    external_id: Optional[str] = Field(None, min_length=0, max_length=50, alias="ExternalID")
    interim_from: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="InterimFrom")
    interim_to: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="InterimTo")
    travel_expenses: Optional[Literal['PublicTransportTrain', 'OwnTransport', 'PublicTransportOther', 'Bicycle', 'None']] = Field(None, alias="TravelExpenses")
    type_of_travel_expenses: Optional[Literal['Other', 'PublicCommonTransport', 'OrganisedCommonTransport']] = Field(None, alias="TypeOfTravelExpenses")
    salary_code_travel_expenses: Optional[int] = Field(None, ge=1, le=9999, alias="SalaryCodeTravelExpenses")

    # Required nested schemas
    address: List[Address] = Field(..., alias="Address")
    family_status: List[FamilyStatus] = Field(..., alias="FamilyStatus")
    contract: List[Contract] = Field(..., alias="Contract")

    # Optional nested schemas
    communication: Optional[List[Communication] | None] = Field(None, alias="Communication")
    tax: Optional[List[Tax] | None] = Field(None, alias="Tax")
    replacement: Optional[List[Replacement] | None] = Field(None, alias="Replacement")

    class Config:
        populate_by_name = True


class WorkerUpdate(BaseModel):
    """Pydantic schema for updating worker data in Sodeco API. Used for PUT operations on /worker/{workerID}. All fields are optional for partial updates."""

    # All fields are optional for updates (only send what needs to be changed)
    worker_number: Optional[int] = Field(None, ge=1, le=9999999, alias="WorkerNumber")
    name: Optional[str] = Field(None, min_length=0, max_length=40, alias="Name")
    first_name: Optional[str] = Field(None, min_length=0, max_length=25, alias="Firstname")
    initial: Optional[str] = Field(None, min_length=1, max_length=1, alias="Initial")
    inss: Optional[float] = Field(None, ge=0.0, le=99999999999.0, alias="INSS")
    sex: Optional[Literal['M', 'F']] = Field(None, alias="Sex")
    birth_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Birthdate")
    birth_place_zip_code: Optional[str] = Field(None, min_length=0, max_length=12, alias="BirthplaceZIPCode")
    birth_place: Optional[str] = Field(None, min_length=0, max_length=30, alias="Birthplace")
    birth_place_country: Optional[str] = Field(None, min_length=5, max_length=5, pattern=r'^[0-9]*$', alias="BirthplaceCountry")
    nationality: Optional[str] = Field(None, min_length=5, max_length=5, pattern=r'^[0-9]*$', alias="Nationality")
    language: Optional[Literal['N', 'F', 'D', 'E']] = Field(None, alias="Language")
    pay_way: Optional[Literal['Cash', 'Transfer', 'Electronic', 'AssignmentList']] = Field(None, alias="PayWay")
    bank_account: Optional[str] = Field(None, min_length=0, max_length=45, alias="BankAccount")
    bic_code: Optional[str] = Field(None, min_length=0, max_length=15, alias="BICCode")
    id: Optional[str] = Field(None, min_length=0, max_length=15, alias="ID")
    id_type: Optional[str] = Field(None, min_length=0, max_length=3, alias="IDType")
    id_valid_until: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="IDValidUntil")
    driver_license: Optional[str] = Field(None, min_length=0, max_length=15, alias="DriverLicense")
    driver_category: Optional[str] = Field(None, min_length=0, max_length=2, alias="DriverCategory")
    number_plate: Optional[str] = Field(None, min_length=0, max_length=10, alias="NumberPlate")
    fuel_card: Optional[str] = Field(None, min_length=0, max_length=20, alias="FuelCard")
    education: Optional[str] = Field(None, min_length=0, max_length=20, alias="Education")
    profession: Optional[str] = Field(None, min_length=0, max_length=50, alias="Profession")
    e_health_insurance: Optional[int] = Field(None, ge=0, le=9999, alias="EHealthInsurance")
    e_health_insurance_reference: Optional[str] = Field(None, min_length=0, max_length=20, alias="EHealthInsuranceReference")
    accident_insurance: Optional[int] = Field(None, ge=0, le=9999, alias="AccidentInsurance")
    medical_center: Optional[int] = Field(None, ge=0, le=9999, alias="MedicalCenter")
    medical_center_reference: Optional[str] = Field(None, min_length=0, max_length=15, alias="MedicalCenterReference")
    external_id: Optional[str] = Field(None, min_length=0, max_length=50, alias="ExternalID")
    interim_from: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="InterimFrom")
    interim_to: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="InterimTo")
    travel_expenses: Optional[Literal['PublicTransportTrain', 'OwnTransport', 'PublicTransportOther', 'Bicycle', 'None']] = Field(None, alias="TravelExpenses")
    type_of_travel_expenses: Optional[Literal['Other', 'PublicCommonTransport', 'OrganisedCommonTransport']] = Field(None, alias="TypeOfTravelExpenses")
    salary_code_travel_expenses: Optional[int] = Field(None, ge=1, le=9999, alias="SalaryCodeTravelExpenses")

    class Config:
        populate_by_name = True
