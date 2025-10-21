from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from enum import Enum
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class ResetEnum(str, Enum):
    N = "N"
    Y = "Y"


class ContractTypeEnum(str, Enum):
    WORKMAN = "Workman"
    EMPLOYEE = "Employee"
    DIRECTOR = "Director"


class WorkingTimeEnum(str, Enum):
    FULLTIME = "Fulltime"
    PARTTIME = "PartTime"


class SpecWorkingTimeEnum(str, Enum):
    REGULAR = "Regular"
    INTERRUPTIONS = "Interruptions"
    SEASONAL_WORKER = "SeasonalWorker"


class AgricultureTypeEnum(str, Enum):
    NONE = None
    HORTICULTURE = "Horticulture"
    HORTICULTURE_CHICORY = "HorticultureChicory"
    AGRICULTURE = "Agriculture"
    HORTICULTURE_MUSHROOM = "HorticultureMushroom"
    HORTICULTURE_FRUIT = "HorticultureFruit"


class CareerBreakKindEnum(str, Enum):
    FULLTIME = "Fulltime"
    PARTTIME_ONE_FIFTH = "PartTimeOneFifth"
    PARTTIME_ONE_QUARTER = "PartTimeOneQuarter"
    PARTTIME_ONE_THIRD = "PartTimeOneThird"
    PARTTIME_HALF = "PartTimeHalf"
    PARTTIME_THREE_FIFTHS = "PartTimeThreeFifths"
    PARTTIME_ONE_TENTH = "PartTimeOneTenth"


class CareerBreakReasonEnum(str, Enum):
    PALLIATIVE_CARE = "PalliativeCare"
    SERIOUSLY_ILL = "SeriouslyIll"
    OTHER = "Other"
    PARENTAL_LEAVE = "ParentalLeave"
    CRISIS = "Crisis"
    FAMILY_CARE = "FamilyCare"
    END_OF_CAREER = "EndOfCareer"
    SICK_CHILD = "SickChild"
    FAMILY_CARE_CORONA = "FamilyCareCorona"
    CHILD_CARE_UNDER_8 = "ChildCareUnder8"
    CHILD_CARE_HANDICAP_UNDER_21 = "ChildCareHandicapUnder21"
    CERTIFIED_TRAINING = "CertifiedTraining"


class DocumentC78Enum(str, Enum):
    NIHIL = "Nihil"
    C783 = "C783"
    C784 = "C784"
    C78_ACTIVA = "C78Activa"
    C78_START = "C78Start"
    C78_SINE = "C78Sine"
    C78_SHORT_TERM = "C78ShortTerm"
    WALLONIA_LONGTERM_JOB_SEEKERS = "WalloniaLongtermJobSeekers"
    WALLONIA_YOUNG_JOB_SEEKERS = "WalloniaYoungJobSeekers"
    WALLONIA_IMPULSION_INSERTION = "WalloniaImpulsionInsertion"
    BRUSSELS_LONGTERM_JOB_SEEKERS = "BrusselsLongtermJobSeekers"
    BRUSSELS_REDUCED_ABILITY = "BrusselsReducedAbility"


class ReducingWorkingKindEnum(str, Enum):
    NIHIL = "Nihil"
    PAID = "Paid"
    UNPAID = "Unpaid"


class SocialBalanceJoblevelEnum(str, Enum):
    OPERATIONAL_STAFF = "OperationalStaff"
    EXECUTIVE_STAFF = "ExecutiveStaff"
    MANAGEMENT_STAFF = "ManagementStaff"
    BY_FUNCTION = "ByFunction"


class TypeOfIndexingEnum(str, Enum):
    NO_INDEXATION = "NoIndexation"
    INDEXATION = "Indexation"
    FROZEN_SALARY = "FrozenSalary"
    SALARY_ABOVE_SCALE = "SalaryAboveScale"


class DimonaStatusEnum(str, Enum):
    BLOCKED = "Blocked"
    IN_PROGRESS = "InProgress"
    OK = "OK"
    ERROR = "Error"


# Contract Literal Types
ContractLiteral = Literal['Usually', 'FlexiVerbal', 'FlexiWritten', 'FlexiLiable', 'Sportsperson', 'Housekeeper', 'Servant', 'Agriculture', 'Homework', 'HomeworkChildcare', 'Physician', 'PhysicianTraining', 'PhysicianIndependant', 'ApprenticeFlemisch', 'ApprenticeFrench', 'ApprenticeGerman', 'ApprenticeManager', 'ApprenticeIndustrial', 'ApprenticeSocio', 'ApprenticeBio', 'ApprenticeAlternating', 'EarlyRetirement', 'EarlyRetirementPartTime', 'FreeNOSS', 'FreeNOSSManager', 'FreeNOSSOther', 'FreeNOSSSportingEvent', 'FreeNOSSHelper', 'FreeNOSSSocio', 'FreeNOSSEducation', 'FreeNOSSSpecialCultures', 'FreeNOSSVolunteer', 'Horeca', 'HorecaExtraHourLiable', 'HorecaExtraDayLiable', 'HorecaExtraHourForfait', 'HorecaExtraDayForfait', 'HorecaFlexiVerbal', 'HorecaFlexiWritten', 'HorecaFlexiLiable', 'Construction', 'ConstructionAlternating', 'ConstructionApprenticeYounger', 'ConstructionApprentice', 'ConstructionGodfather', 'JobTrainingIBO', 'JobTrainingSchool', 'JobTrainingVDAB', 'JobTrainingLiberalProfession', 'JobTrainingEntry', 'JobTrainingPFIWa', 'JobTrainingABO', 'JobTrainingPFIBx', 'JobTrainingBIO', 'JobTrainingAlternating', 'JobTrainingDisability', 'NonProfitRiziv', 'NonProfitGesco', 'NonProfitDAC', 'NonProfitPrime', 'NonProfitLowSkilled', 'Artist', 'ArtistWithContract', 'ArtistWithoutContract', 'Transport', 'TransportNonMobile', 'TransportGarage', 'Aircrew', 'AircrewPilot', 'AircrewCabinCrew', 'Interim', 'InterimTemporary', 'InterimsPermanent', 'External', 'ExternalApplicant', 'ExternalSubcontractor', 'ExternalAgentIndependant', 'ExternalExtern', 'ExternalIntern', 'ExternalLegalPerson', 'SalesRepresentative', 'SportsTrainer']


# Nested Models
class UsingData(BaseModel):
    using_joint_commission_nbr: Optional[str] = Field(None, alias="UsingJointCommissionNbr", description="Using joint commission number", example="123", min_length=3, max_length=3, pattern=r'^[0-9,.]*$')
    using_employer_name: Optional[str] = Field(None, alias="UsingEmployerName", description="Using employer name", example="Acme Corp", max_length=40)
    using_employer_company_id: Optional[float] = Field(None, alias="UsingEmployerCompanyID", description="Using employer company ID", example=1234567890.0, ge=0, le=9999999999)
    using_street: Optional[str] = Field(None, alias="UsingStreet", description="Using street", example="Main Street", max_length=100)
    using_house_number: Optional[str] = Field(None, alias="UsingHouseNumber", description="Using house number", example="123", max_length=10)
    using_post_box: Optional[str] = Field(None, alias="UsingPostBox", description="Using post box", example="12345", max_length=5)
    using_zip_code: Optional[str] = Field(None, alias="UsingZIPCode", description="Using ZIP code", example="1000", max_length=12)
    using_city: Optional[str] = Field(None, alias="UsingCity", description="Using city", example="Brussels", max_length=30)
    using_country: Optional[str] = Field("00150", alias="UsingCountry", description="Using country code", example="00150", min_length=5, max_length=5, pattern=r'^[0-9]*$')

    class Config:
        populate_by_name = True


class CareerBreakDefinition(BaseModel):
    exist: ResetEnum = Field(alias="Exist", description="Career break exists", example="N")
    kind: Optional[CareerBreakKindEnum] = Field(None, alias="Kind", description="Career break kind", example="Fulltime")
    reason: Optional[CareerBreakReasonEnum] = Field(None, alias="Reason", description="Career break reason", example="ParentalLeave")
    originally_contract_type: Optional[str] = Field(None, alias="OriginallyContractType", description="Originally contract type", example="Fulltime")
    weekhours_worker_before: Optional[float] = Field(None, alias="WeekhoursWorkerBefore", description="Weekly hours worker before", example=40.0)
    weekhours_employer_before: Optional[float] = Field(None, alias="WeekhoursEmployerBefore", description="Weekly hours employer before", example=40.0)

    class Config:
        populate_by_name = True


class CertainWorkDefinition(BaseModel):
    exist: ResetEnum = Field(alias="Exist", description="Certain work exists", example="N")
    description: Optional[str] = Field(None, alias="Description", description="Certain work description", example="Special project work", max_length=250)

    class Config:
        populate_by_name = True


class ClsDimona(BaseModel):
    dimona_period_id: Optional[float] = Field(None, alias="DimonaPeriodId", description="DIMONA period ID", example=123456789.0, ge=0, le=999999999999)
    starting_date: str = Field(alias="StartingDate", description="Starting date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    ending_date: Optional[str] = Field(None, alias="EndingDate", description="Ending date in YYYYMMDD format", example="20251231", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    starting_hour: Optional[str] = Field(None, alias="StartingHour", description="Starting hour", example="080000000000", min_length=12, max_length=12, pattern=r'^[0-9]*$')
    ending_hour: Optional[str] = Field(None, alias="EndingHour", description="Ending hour", example="170000000000", min_length=12, max_length=12, pattern=r'^[0-9]*$')
    starting_hour2: Optional[str] = Field(None, alias="StartingHour2", description="Starting hour 2", example="080000000000", min_length=12, max_length=12, pattern=r'^[0-9]*$')
    ending_hour2: Optional[str] = Field(None, alias="EndingHour2", description="Ending hour 2", example="170000000000", min_length=12, max_length=12, pattern=r'^[0-9]*$')
    first_month_c32a_nbr: Optional[float] = Field(None, alias="FirstMonthC32ANbr", description="First month C32A number", example=123456789.0, ge=0, le=999999999999)
    next_month_c32a_nbr: Optional[float] = Field(None, alias="NextMonthC32ANbr", description="Next month C32A number", example=123456789.0, ge=0, le=999999999999)
    planned_hours_nbr: Optional[int] = Field(None, alias="PlannedHoursNbr", description="Planned hours number", example=40, ge=0, le=999)
    using_data: Optional[UsingData] = Field(None, alias="UsingData", description="Using data")
    receipt: Optional[float] = Field(None, alias="Receipt", description="Receipt", example=123456789.0, ge=0, le=999999999999)
    joint_commission_nbr: Optional[str] = Field(None, alias="JointCommissionNbr", description="Joint commission number", example="123456", min_length=3, max_length=6, pattern=r'^[0-9,.]*$')
    worker_type: Optional[str] = Field(None, alias="WorkerType", description="Worker type", example="EMP", min_length=3, max_length=3)
    last_action: Optional[str] = Field(None, alias="LastAction", description="Last action", example="A", min_length=1, max_length=1)
    exceeding_hours_nbr: Optional[int] = Field(None, alias="ExceedingHoursNbr", description="Exceeding hours number", example=5, ge=0, le=999)
    quota_exceeded: Optional[ResetEnum] = Field(None, alias="QuotaExceeded", description="Quota exceeded", example="N")
    belated: Optional[ResetEnum] = Field(None, alias="Belated", description="Belated", example="N")
    status: Optional[DimonaStatusEnum] = Field(None, alias="Status", description="DIMONA status", example="OK")
    error: Optional[str] = Field(None, alias="Error", description="Error message", example="")

    class Config:
        populate_by_name = True


class SalaryCompositionDefinition(BaseModel):
    start_date: str = Field(alias="Startdate", description="Start date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    end_date: Optional[str] = Field(None, alias="Enddate", description="End date in YYYYMMDD format", example="20251231", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    code: int = Field(alias="Code", description="Salary composition code", example=1001, ge=1, le=8999)
    days: Optional[int] = Field(None, alias="Days", description="Days", example=22, ge=0, le=9999)
    hours: Optional[float] = Field(None, alias="Hours", description="Hours", example=176.0, ge=0, le=9999)
    unity: Optional[float] = Field(None, alias="Unity", description="Unity", example=1.0)
    percentage: Optional[float] = Field(None, alias="Percentage", description="Percentage", example=100.0)
    amount: Optional[float] = Field(None, alias="Amount", description="Amount", example=3000.0)
    supplement: Optional[float] = Field(None, alias="Supplement", description="Supplement", example=300.0)
    type_of_indexing: Optional[TypeOfIndexingEnum] = Field(None, alias="TypeOfIndexing", description="Type of indexing", example="NoIndexation")

    class Config:
        populate_by_name = True


# Pydantic schemas for API requests
class ContractCreate(BaseModel):
    """Schema for creating a new contract entry."""

    start_date: str = Field(alias="Startdate", description="Contract start date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    end_date: Optional[str] = Field(None, alias="Enddate", description="Contract end date in YYYYMMDD format", example="20251231", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    employment_status: Optional[ContractTypeEnum] = Field(None, alias="EmploymentStatus", description="Employment status type", example="Employee")
    contract: Optional[ContractLiteral] = Field(None, alias="Contract", description="Contract type code", example="Usually")
    cat_rsz: Optional[str] = Field(None, alias="CatRSZ", description="Social security category code", example="123", min_length=3, max_length=3, pattern=r'^[0-9]*$')
    par_com: Optional[str] = Field(None, alias="ParCom", description="Parity committee code", example="123.45", min_length=3, max_length=10, pattern=r'^[0-9. ]*$')
    document_c78: Optional[DocumentC78Enum] = Field(None, alias="DocumentC78", description="Document C78 status", example="Nihil")
    code_c98: Optional[ResetEnum] = Field(None, alias="CodeC98", description="Code C98 flag", example="N")
    code_c131a: Optional[ResetEnum] = Field(None, alias="CodeC131A", description="Code C131A flag", example="N")
    code_c131a_request_ft: Optional[ResetEnum] = Field(None, alias="CodeC131ARequestFT", description="Code C131A request full-time flag", example="N")
    code_c131: Optional[ResetEnum] = Field(None, alias="CodeC131", description="Code C131 flag", example="N")
    risk: Optional[str] = Field(None, alias="Risk", description="Risk code", example="RISK001", max_length=10)
    social_security_card: Optional[str] = Field(None, alias="SocialSecurityCard", description="Social security card number", example="123456789012345", max_length=15)
    work_permit: Optional[str] = Field(None, alias="WorkPermit", description="Work permit number", example="WP123456789", max_length=15)
    date_in_service: Optional[str] = Field(None, alias="DateInService", description="Date in service in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    seniority: Optional[str] = Field(None, alias="Seniority", description="Seniority date in YYYYMMDD format", example="20200101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    date_professional_experience: Optional[str] = Field(None, alias="DateProfessionalExperience", description="Date professional experience in YYYYMMDD format", example="20200101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    scale_salary_seniority: Optional[str] = Field(None, alias="ScaleSalarySeniority", description="Scale salary seniority date in YYYYMMDD format", example="20200101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    start_probation_period: Optional[str] = Field(None, alias="StartProbationPeriod", description="Start probation period in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    end_probation_period: Optional[str] = Field(None, alias="EndProbationPeriod", description="End probation period in YYYYMMDD format", example="20250401", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    fixed_term: Optional[ResetEnum] = Field(None, alias="FixedTerm", description="Fixed term flag", example="N")
    end_fixed_term: Optional[str] = Field(None, alias="EndFixedTerm", description="End fixed term in YYYYMMDD format", example="20251231", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    date_out_service: Optional[str] = Field(None, alias="DateOutService", description="Date out service in YYYYMMDD format", example="20251231", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    reason_out: Optional[str] = Field(None, alias="ReasonOut", description="Reason out", example="Resignation")
    working_time: Optional[WorkingTimeEnum] = Field(None, alias="WorkingTime", description="Working time type", example="Fulltime")
    spec_working_time: Optional[SpecWorkingTimeEnum] = Field(None, alias="SpecWorkingTime", description="Special working time type", example="Regular")
    schedule: Optional[str] = Field(None, alias="Schedule", description="Schedule code", example="SCH1", max_length=4)
    weekhours_worker: Optional[float] = Field(None, alias="WeekhoursWorker", description="Weekly hours for worker", example=40.0, ge=1, le=50)
    weekhours_employer: Optional[float] = Field(None, alias="WeekhoursEmployer", description="Weekly hours for employer", example=40.0, ge=1, le=50)
    weekhours_worker_average: Optional[float] = Field(None, alias="WeekhoursWorkerAverage", description="Weekly hours worker average", example=40.0, ge=1, le=50)
    weekhours_employer_average: Optional[float] = Field(None, alias="WeekhoursEmployerAverage", description="Weekly hours employer average", example=40.0, ge=1, le=50)
    weekhours_worker_effective: Optional[float] = Field(None, alias="WeekhoursWorkerEffective", description="Weekly hours worker effective", example=40.0, ge=1, le=50)
    weekhours_employer_effective: Optional[float] = Field(None, alias="WeekhoursEmployerEffective", description="Weekly hours employer effective", example=40.0, ge=1, le=50)
    days_week: Optional[float] = Field(None, alias="DaysWeek", description="Days per week", example=5.0)
    days_week_ft: Optional[float] = Field(None, alias="DaysWeekFT", description="Days per week full time", example=5.0)
    reducing_working_kind: Optional[ReducingWorkingKindEnum] = Field(None, alias="ReducingWorkingKind", description="Reducing working kind", example="Nihil")
    reducing_working_kind_days: Optional[float] = Field(None, alias="ReducingWorkingKindDays", description="Reducing working kind days", example=0.0)
    reducing_working_kind_hours: Optional[float] = Field(None, alias="ReducingWorkingKindHours", description="Reducing working kind hours", example=0.0)
    part_time_return_towork: Optional[str] = Field(None, alias="PartTimeReturnTowork", description="Part time return to work", example="PT01", max_length=4)
    asr_schedule: Optional[str] = Field(None, alias="ASRSchedule", description="ASR schedule", example="AS", max_length=2)
    proff_cat: Optional[str] = Field(None, alias="ProffCat", description="Professional category", example="PROF001", max_length=10)
    function: Optional[str] = Field(None, alias="Function", description="Function code", example="FUNC001", max_length=10)
    function_description: Optional[str] = Field(None, alias="FunctionDescription", description="Function description", example="Software Developer", max_length=50)
    social_balance_joblevel: Optional[SocialBalanceJoblevelEnum] = Field(None, alias="SocialBalanceJoblevel", description="Social balance job level", example="ExecutiveStaff")
    office: Optional[int] = Field(None, alias="Office", description="Office code", example=1)
    division: Optional[str] = Field(None, alias="Division", description="Division code", example="DIV001", max_length=10)
    invoicing_division: Optional[str] = Field(None, alias="InvoicingDivision", description="Invoicing division code", example="INV001", max_length=10)
    cost_centre: Optional[str] = Field(None, alias="CostCentre", description="Cost centre code", example="CC001", max_length=15)
    scale_salary_prisma: Optional[ResetEnum] = Field(None, alias="ScaleSalaryPrisma", description="Scale salary prisma", example="N")
    scale_salary_use: Optional[ResetEnum] = Field(None, alias="ScaleSalaryUse", description="Scale salary use", example="N")
    scale_salary_definition: Optional[str] = Field(None, alias="ScaleSalaryDefinition", description="Scale salary definition", example="SCALE001", max_length=10)
    scale_salary_category: Optional[str] = Field(None, alias="ScaleSalaryCategory", description="Scale salary category", example="CAT001", max_length=10)
    scale_salary_scale: Optional[str] = Field(None, alias="ScaleSalaryScale", description="Scale salary scale", example="SCALE_DEFINITION", max_length=100)
    exclude_for_dmfa_declaration: Optional[ResetEnum] = Field(None, alias="ExcludeForDmfaDeclaration", description="Exclude for DMFA declaration", example="N")
    agriculture_type: Optional[AgricultureTypeEnum] = Field(None, alias="AgricultureType", description="Agriculture type", example="Agriculture")
    no_dimona: Optional[ResetEnum] = Field(None, alias="NoDimona", description="No DIMONA flag", example="N")
    no_dmfa: Optional[ResetEnum] = Field(None, alias="NoDmfa", description="No DMFA flag", example="N")
    no_asrdrs: Optional[ResetEnum] = Field(None, alias="NoAsrdrs", description="No ASRDRS flag", example="N")
    security: Optional[str] = Field(None, alias="Security", description="Security code", example="SEC001", max_length=10)

    # Nested models
    career_break: Optional[CareerBreakDefinition] = Field(None, alias="CareerBreak", description="Career break definition")
    certain_work: Optional[CertainWorkDefinition] = Field(None, alias="CertainWork", description="Certain work definition")
    dimona: Optional[ClsDimona] = Field(None, alias="Dimona", description="DIMONA definition")
    salary_compositions: Optional[List[SalaryCompositionDefinition]] = Field(None, alias="SalaryCompositions", description="Salary compositions")

    class Config:
        populate_by_name = True


class ContractUpdate(ContractCreate):
    """Schema for updating a contract entry."""
    # Make Startdate optional for updates
    start_date: Optional[str] = Field(None, alias="Startdate", description="Contract start date in YYYYMMDD format", example="20250101", min_length=8, max_length=8, pattern=r'^[0-9]*$')
    class Config:
        populate_by_name = True


# Pandera schema for DataFrame validation
class ContractGet(BrynQPanderaDataFrameModel):
    """Schema for validating contract data from API."""

    # Required fields
    start_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Contract start date in YYYYMMDD format", alias="Startdate")

    # Optional fields - contract basic info
    worker_number: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=False, description="Worker number reference", alias="WorkerNumber")
    end_date: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Contract end date in YYYYMMDD format", alias="Enddate")
    employment_status: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Employment status type", alias="EmploymentStatus")
    contract: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Contract type code", alias="Contract")

    # Social security fields
    cat_rsz: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Social security category code", alias="CatRSZ")
    par_com: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Parity committee code", alias="ParCom")
    document_c78: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Document C78 status", alias="DocumentC78")
    code_c98: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Code C98 flag", alias="CodeC98")
    code_c131a: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Code C131A flag", alias="CodeC131A")
    code_c131a_request_ft: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Code C131A request full-time flag", alias="CodeC131ARequestFT")
    code_c131: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Code C131 flag", alias="CodeC131")
    risk: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Risk code", alias="Risk")
    social_security_card: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Social security card number", alias="SocialSecurityCard")
    work_permit: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Work permit number", alias="WorkPermit")

    # Date fields
    date_in_service: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Date in service in YYYYMMDD format", alias="DateInService")
    seniority: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Seniority date in YYYYMMDD format", alias="Seniority")
    date_professional_experience: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Date professional experience in YYYYMMDD format", alias="DateProfessionalExperience")
    scale_salary_seniority: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Scale salary seniority date in YYYYMMDD format", alias="ScaleSalarySeniority")
    start_probation_period: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Start probation period in YYYYMMDD format", alias="StartProbationPeriod")
    end_probation_period: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="End probation period in YYYYMMDD format", alias="EndProbationPeriod")
    fixed_term: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Fixed term flag", alias="FixedTerm")
    end_fixed_term: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="End fixed term in YYYYMMDD format", alias="EndFixedTerm")
    date_out_service: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Date out service in YYYYMMDD format", alias="DateOutService")
    reason_out: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Reason out", alias="ReasonOut")

    # Working time fields
    working_time: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Working time type", alias="WorkingTime")
    spec_working_time: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Special working time type", alias="SpecWorkingTime")
    schedule: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Schedule code", alias="Schedule")
    weekhours_worker: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Weekly hours for worker", alias="WeekhoursWorker")
    weekhours_employer: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Weekly hours for employer", alias="WeekhoursEmployer")
    weekhours_worker_average: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Weekly hours worker average", alias="WeekhoursWorkerAverage")
    weekhours_employer_average: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Weekly hours employer average", alias="WeekhoursEmployerAverage")
    weekhours_worker_effective: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Weekly hours worker effective", alias="WeekhoursWorkerEffective")
    weekhours_employer_effective: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Weekly hours employer effective", alias="WeekhoursEmployerEffective")
    days_week: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Days per week", alias="DaysWeek")
    days_week_ft: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Days per week full time", alias="DaysWeekFT")
    reducing_working_kind: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Reducing working kind", alias="ReducingWorkingKind")
    reducing_working_kind_days: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Reducing working kind days", alias="ReducingWorkingKindDays")
    reducing_working_kind_hours: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Reducing working kind hours", alias="ReducingWorkingKindHours")
    part_time_return_towork: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Part time return to work", alias="PartTimeReturnTowork")
    asr_schedule: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="ASR schedule", alias="ASRSchedule")

    # Job and function fields
    proff_cat: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Professional category", alias="ProffCat")
    function: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Function code", alias="Function")
    function_description: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Function description", alias="FunctionDescription")
    social_balance_joblevel: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Social balance job level", alias="SocialBalanceJoblevel")
    office: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Office code", alias="Office")
    division: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Division code", alias="Division")
    invoicing_division: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Invoicing division code", alias="InvoicingDivision")
    cost_centre: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Cost centre code", alias="CostCentre")

    # Salary scale fields
    scale_salary_prisma: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Scale salary prisma", alias="ScaleSalaryPrisma")
    scale_salary_use: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Scale salary use", alias="ScaleSalaryUse")
    scale_salary_definition: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Scale salary definition", alias="ScaleSalaryDefinition")
    scale_salary_category: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Scale salary category", alias="ScaleSalaryCategory")
    scale_salary_scale: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Scale salary scale", alias="ScaleSalaryScale")

    # Other fields
    agriculture_type: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Agriculture type", alias="AgricultureType")
    no_dimona: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="No DIMONA flag", alias="NoDimona")
    no_dmfa: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="No DMFA flag", alias="NoDMFA")
    no_asrdrs: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="No ASRDRS flag", alias="NoASRDRS")
    security: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Security code", alias="Security")
    exclude_for_dmfa_declaration: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Exclude for DMFA declaration", alias="ExcludeForDmfaDeclaration")

    # Nested fields - SectorSeniority (normalized)
    sector_seniority: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Sector seniority", alias="SectorSeniority")

    # Nested fields - Student (normalized)
    student_exist: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Student exist", alias="Student__Exist")
    student_solidarity_contribution: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Student solidarity contribution", alias="Student__SolidarityContribution")

    # Nested fields - SalaryCompositions (keep as single field)
    salary_compositions: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Salary compositions data", alias="SalaryCompositions")

    # Nested fields - SubstituteContract (normalized)
    substitute_contract: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Substitute contract", alias="SubstituteContract")

    # Nested fields - CareerBreak (normalized)
    career_break_exist: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Career break exist", alias="CareerBreak__Exist")
    career_break_kind: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Career break kind", alias="CareerBreak__Kind")
    career_break_reason: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Career break reason", alias="CareerBreak__Reason")
    career_break_originally_contract_type: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Career break originally contract type", alias="CareerBreak__OriginallyContractType")
    career_break_weekhours_worker_before: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Career break weekhours worker before", alias="CareerBreak__WeekhoursWorkerBefore")
    career_break_weekhours_employer_before: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Career break weekhours employer before", alias="CareerBreak__WeekhoursEmployerBefore")

    # Nested fields - Retired (normalized)
    retired_exist: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Retired exist", alias="Retired__Exist")
    retired_kind: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Retired kind", alias="Retired__Kind")
    retired_date_retired: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Retired date retired", alias="Retired__DateRetired")
    retired_apply_collecting_2nd_pension_pillar: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Retired apply collecting 2nd pension pillar", alias="Retired__ApplyCollecting2ndPensionPillar")
    retired_retired_type: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Retired retired type", alias="Retired__RetiredType")

    # Nested fields - ProtectedEmployee (normalized)
    protected_employee_exist: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Protected employee exist", alias="ProtectedEmployee__Exist")
    protected_employee_reason: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Protected employee reason", alias="ProtectedEmployee__Reason")
    protected_employee_start_date: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Protected employee start date", alias="ProtectedEmployee__Startdate")
    protected_employee_end_date: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Protected employee end date", alias="ProtectedEmployee__Enddate")

    # Nested fields - Sportsperson (normalized)
    sportsperson_exist: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Sportsperson exist", alias="Sportsperson__Exist")
    sportsperson_recognized_foreign_sportsperson: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Sportsperson recognized foreign sportsperson", alias="Sportsperson__RecognizedForeignSportsperson")
    sportsperson_opportunity_contract: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Sportsperson opportunity contract", alias="Sportsperson__OpportunityContract")

    # Nested fields - CertainWork (normalized)
    certain_work_exist: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Certain work exist", alias="CertainWork__Exist")
    certain_work_description: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Certain work description", alias="CertainWork__Description")

    # Nested fields - MethodOfRemuneration (normalized)
    method_of_remuneration_exist: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Method of remuneration exist", alias="MethodOfRemuneration__Exist")
    method_of_remuneration_remuneration: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Method of remuneration remuneration", alias="MethodOfRemuneration__Remuneration")
    method_of_remuneration_payment: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Method of remuneration payment", alias="MethodOfRemuneration__Payment")

    # Nested fields - InternationalEmployment (normalized)
    international_employment_exist: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="International employment exist", alias="InternationalEmployment__Exist")
    international_employment_kind: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="International employment kind", alias="InternationalEmployment__Kind")
    international_employment_border_country: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="International employment border country", alias="InternationalEmployment__BorderCountry")

    # Nested fields - Dimona (normalized)
    dimona_dimona_period_id: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Dimona period ID", alias="Dimona__DimonaPeriodId")
    dimona_starting_date: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Dimona starting date", alias="Dimona__StartingDate")
    dimona_ending_date: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Dimona ending date", alias="Dimona__EndingDate")
    dimona_starting_hour: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Dimona starting hour", alias="Dimona__StartingHour")
    dimona_ending_hour: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Dimona ending hour", alias="Dimona__EndingHour")
    dimona_starting_hour2: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Dimona starting hour 2", alias="Dimona__StartingHour2")
    dimona_ending_hour2: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Dimona ending hour 2", alias="Dimona__EndingHour2")
    dimona_first_month_c32a_nbr: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Dimona first month C32A number", alias="Dimona__FirstMonthC32ANbr")
    dimona_next_month_c32a_nbr: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Dimona next month C32A number", alias="Dimona__NextMonthC32ANbr")
    dimona_planned_hours_nbr: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Dimona planned hours number", alias="Dimona__PlannedHoursNbr")
    dimona_receipt: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Dimona receipt", alias="Dimona__Receipt")
    dimona_joint_commission_nbr: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Dimona joint commission number", alias="Dimona__JointCommissionNbr")
    dimona_worker_type: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Dimona worker type", alias="Dimona__WorkerType")
    dimona_last_action: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Dimona last action", alias="Dimona__LastAction")
    dimona_exceeding_hours_nbr: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Dimona exceeding hours number", alias="Dimona__ExceedingHoursNbr")
    dimona_quota_exceeded: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Dimona quota exceeded", alias="Dimona__QuotaExceeded")
    dimona_belated: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Dimona belated", alias="Dimona__Belated")
    dimona_status: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Dimona status", alias="Dimona__Status")
    dimona_error: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Dimona error", alias="Dimona__Error")

    # Nested fields - ProgressiveWorkResumption (normalized)
    progressive_work_resumption_progressive_work_resumption: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption", alias="ProgressiveWorkResumption__ProgressiveWorkResumption")
    progressive_work_resumption_exist: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption exist", alias="ProgressiveWorkResumption__Exist")
    progressive_work_resumption_risk: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption risk", alias="ProgressiveWorkResumption__Risk")
    progressive_work_resumption_hours: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption hours", alias="ProgressiveWorkResumption__Hours")
    progressive_work_resumption_minutes: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption minutes", alias="ProgressiveWorkResumption__Minutes")
    progressive_work_resumption_days: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption days", alias="ProgressiveWorkResumption__Days")
    progressive_work_resumption_start_date_illness: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption start date illness", alias="ProgressiveWorkResumption__StartdateIllness")
    progressive_work_resumption_comment: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption comment", alias="ProgressiveWorkResumption__Comment")
    progressive_work_resumption_start_date: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption start date", alias="ProgressiveWorkResumption__StartDate")
    progressive_work_resumption_end_date: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption end date", alias="ProgressiveWorkResumption__EndDate")
    progressive_work_resumption_percentage: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Progressive work resumption percentage", alias="ProgressiveWorkResumption__Percentage")

    # Social security
    cat_rsz: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Social security category code", alias="CatRSZ")
    par_com: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Parity committee code", alias="ParCom")
    document_c78: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Document C78 status", alias="DocumentC78")
    code_c98: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Code C98 flag", alias="CodeC98")
    code_c131a: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Code C131A flag", alias="CodeC131A")
    code_c131a_request_ft: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Code C131A request full-time flag", alias="CodeC131ARequestFT")
    code_c131: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Code C131 flag", alias="CodeC131")
    risk: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Risk code", alias="Risk")
    social_security_card: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Social security card number", alias="SocialSecurityCard")
    work_permit: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Work permit number", alias="WorkPermit")

    # Dates
    date_in_service: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Date in service in YYYYMMDD format", alias="DateInService")
    seniority: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Seniority date in YYYYMMDD format", alias="Seniority")
    date_professional_experience: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Date professional experience in YYYYMMDD format", alias="DateProfessionalExperience")
    scale_salary_seniority: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Scale salary seniority date in YYYYMMDD format", alias="ScaleSalarySeniority")
    start_probation_period: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Start probation period in YYYYMMDD format", alias="StartProbationPeriod")
    end_probation_period: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="End probation period in YYYYMMDD format", alias="EndProbationPeriod")
    end_fixed_term: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="End fixed term in YYYYMMDD format", alias="EndFixedTerm")
    date_out_service: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Date out service in YYYYMMDD format", alias="DateOutService")
    reason_out: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Reason out", alias="ReasonOut")

    # Working time
    working_time: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Working time type", alias="WorkingTime")
    spec_working_time: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Special working time type", alias="SpecWorkingTime")
    schedule: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Schedule code", alias="Schedule")
    weekhours_worker: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Weekly hours for worker", alias="WeekhoursWorker")
    weekhours_employer: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Weekly hours for employer", alias="WeekhoursEmployer")
    weekhours_worker_average: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Weekly hours worker average", alias="WeekhoursWorkerAverage")
    weekhours_employer_average: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Weekly hours employer average", alias="WeekhoursEmployerAverage")
    weekhours_worker_effective: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Weekly hours worker effective", alias="WeekhoursWorkerEffective")
    weekhours_employer_effective: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Weekly hours employer effective", alias="WeekhoursEmployerEffective")
    days_week: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Days per week", alias="DaysWeek")
    days_week_ft: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Days per week full time", alias="DaysWeekFT")
    reducing_working_kind: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Reducing working kind", alias="ReducingWorkingKind")
    reducing_working_kind_days: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Reducing working kind days", alias="ReducingWorkingKindDays")
    reducing_working_kind_hours: Optional[Series[pd.Float64Dtype]] = pa.Field(coerce=True, nullable=True, description="Reducing working kind hours", alias="ReducingWorkingKindHours")
    part_time_return_towork: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Part time return to work", alias="PartTimeReturnTowork")
    asr_schedule: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="ASR schedule", alias="ASRSchedule")

    # Function and organization
    proff_cat: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Professional category", alias="ProffCat")
    function: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Function code", alias="Function")
    function_description: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Function description", alias="FunctionDescription")
    social_balance_joblevel: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Social balance job level", alias="SocialBalanceJoblevel")
    office: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Office code", alias="Office")
    division: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Division code", alias="Division")
    invoicing_division: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Invoicing division code", alias="InvoicingDivision")
    cost_centre: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Cost centre code", alias="CostCentre")

    # Salary and scales
    scale_salary_prisma: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Scale salary prisma", alias="ScaleSalaryPrisma")
    scale_salary_use: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Scale salary use", alias="ScaleSalaryUse")
    scale_salary_definition: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Scale salary definition", alias="ScaleSalaryDefinition")
    scale_salary_category: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Scale salary category", alias="ScaleSalaryCategory")
    scale_salary_scale: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Scale salary scale", alias="ScaleSalaryScale")

    # Flags
    fixed_term: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Fixed term flag", alias="FixedTerm")
    exclude_for_dmfa_declaration: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Exclude for DMFA declaration", alias="ExcludeForDmfaDeclaration")
    agriculture_type: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Agriculture type", alias="AgricultureType")
    no_dimona: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="No DIMONA flag", alias="NoDimona")
    no_dmfa: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="No DMFA flag", alias="NoDmfa")
    no_asrdrs: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="No ASRDRS flag", alias="NoAsrdrs")
    security: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Security code", alias="Security")

    class _Annotation:
        primary_key = "worker_number"
