from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


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


class UsingData(BaseModel):
    """Model for using data in contracts"""
    using_joint_commission_nbr: Optional[str] = Field(None, min_length=3, max_length=3, pattern=r'^[0-9,.]*$', alias="UsingJointCommissionNbr")
    using_employer_name: Optional[str] = Field(None, min_length=0, max_length=40, alias="UsingEmployerName")
    using_employer_company_id: Optional[float] = Field(None, ge=0, le=9999999999, alias="UsingEmployerCompanyID")
    using_street: Optional[str] = Field(None, min_length=0, max_length=100, alias="UsingStreet")
    using_house_number: Optional[str] = Field(None, min_length=0, max_length=10, alias="UsingHouseNumber")
    using_post_box: Optional[str] = Field(None, min_length=0, max_length=5, alias="UsingPostBox")
    using_zip_code: Optional[str] = Field(None, min_length=0, max_length=12, alias="UsingZIPCode")
    using_city: Optional[str] = Field(None, min_length=0, max_length=30, alias="UsingCity")
    using_country: Optional[str] = Field("00150", min_length=5, max_length=5, pattern=r'^[0-9]*$', alias="UsingCountry")


class CareerBreakDefinition(BaseModel):
    """Model for career break entries"""
    exist: ResetEnum
    kind: Optional[str] = Field(None, enum=[
        "Fulltime", "PartTimeOneFifth", "PartTimeOneQuarter", "PartTimeOneThird",
        "PartTimeHalf", "PartTimeThreeFifths", "PartTimeOneTenth"
    ], alias="Kind")
    reason: Optional[str] = Field(None, enum=[
        "PalliativeCare", "SeriouslyIll", "Other", "ParentalLeave", "Crisis",
        "FamilyCare", "EndOfCareer", "SickChild", "FamilyCareCorona",
        "ChildCareUnder8", "ChildCareHandicapUnder21", "CertifiedTraining"
    ], alias="Reason")
    originally_contract_type: Optional[WorkingTimeEnum] = None
    weekhours_worker_before: Optional[float] = None
    weekhours_employer_before: Optional[float] = None


class CertainWorkDefinition(BaseModel):
    """Model for certain work entries"""
    exist: ResetEnum
    description: Optional[str] = Field(None, min_length=0, max_length=250, alias="Description")


class ClsDimona(BaseModel):
    """Model for Dimona entries"""
    dimona_period_id: Optional[float] = Field(None, ge=0, le=999999999999, alias="DimonaPeriodId")
    starting_date: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="StartingDate")
    ending_date: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="EndingDate")
    starting_hour: Optional[str] = Field(None, min_length=12, max_length=12, pattern=r'^[0-9]*$', alias="StartingHour")
    ending_hour: Optional[str] = Field(None, min_length=12, max_length=12, pattern=r'^[0-9]*$', alias="EndingHour")
    starting_hour2: Optional[str] = Field(None, min_length=12, max_length=12, pattern=r'^[0-9]*$')
    ending_hour2: Optional[str] = Field(None, min_length=12, max_length=12, pattern=r'^[0-9]*$', alias="EndingHour2")
    first_month_c32a_nbr: Optional[float] = Field(None, ge=0, le=999999999999, alias="FirstMonthC32ANbr")
    next_month_c32a_nbr: Optional[float] = Field(None, ge=0, le=999999999999, alias="NextMonthC32ANbr")
    planned_hours_nbr: Optional[int] = Field(None, ge=0, le=999, alias="PlannedHoursNbr")
    using_data: Optional[UsingData] = None
    receipt: Optional[float] = Field(None, ge=0, le=999999999999, alias="Receipt")
    joint_commission_nbr: Optional[str] = Field(None, min_length=3, max_length=6, pattern=r'^[0-9,.]*$', alias="JointCommissionNbr")
    worker_type: Optional[str] = Field(None, min_length=3, max_length=3, alias="WorkerType")
    last_action: Optional[str] = Field(None, min_length=1, max_length=1, alias="LastAction")
    exceeding_hours_nbr: Optional[int] = Field(None, ge=0, le=999, alias="ExceedingHoursNbr")
    quota_exceeded: Optional[ResetEnum] = None
    belated: Optional[ResetEnum] = None
    status: Optional[str] = Field(None, enum=["Blocked", "InProgress", "OK", "Error"], alias="Status")
    error: Optional[str] = None


class clsSalaryComposition(BaseModel):
    """Model for salary composition entries"""
    startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    code: int = Field(..., ge=1, le=8999, alias="Code")
    enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Enddate")
    days: Optional[int] = Field(None, ge=0, le=99, alias="Days")
    hours: Optional[float] = Field(None, ge=0, le=9999, alias="Hours")
    unity: Optional[float] = None
    percentage: Optional[float] = None
    amount: Optional[float] = None
    supplement: Optional[float] = None
    type_of_indexing: Optional[str] = Field(None, enum=[
        "NoIndexation", "Indexation", "FrozenSalary", "SalaryAboveScale"
    ], alias="TypeOfIndexing")


class InternationalEmploymentDefinition(BaseModel):
    """Model for international employment entries"""
    exist: ResetEnum
    kind: Optional[str] = Field(None, enum=[
        "SecondmentFrom", "SalarySplit", "FrontierWorker", "SecondmentTo"
    ], alias="Kind")
    border_country: Optional[str] = Field("00111", min_length=5, max_length=5, pattern=r'^[0-9]*$', alias="BorderCountry")


class MethodOfRemunerationDefinition(BaseModel):
    """Model for remuneration method entries"""
    exist: ResetEnum
    remuneration: Optional[str] = Field(None, enum=["Commission", "Piece", "ServiceVouchers"], alias="Remuneration")
    payment: Optional[str] = Field(None, enum=["Fixed", "Variable", "Mixed"], alias="Payment")


class ProgressiveWorkResumptionDefinition(BaseModel):
    """Model for progressive work resumption entries"""
    exist: ResetEnum
    risk: Optional[str] = Field(None, enum=["IncapacityForWork", "MaternityProtection"], alias="Risk")
    hours: Optional[int] = Field(None, ge=0, le=40, alias="Hours")
    minutes: Optional[int] = Field(None, ge=0, le=60, alias="Minutes")
    days: Optional[float] = Field(None, ge=0, le=5, alias="Days")
    startdate_illness: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="StartdateIllness")
    comment: Optional[str] = Field(None, min_length=0, max_length=200, alias="Comment")


class ProtectedEmployeeDefinition(BaseModel):
    """Model for protected employee entries"""
    exist: ResetEnum
    reason: Optional[str] = Field(None, min_length=4, max_length=4, pattern=r'^[0-9]*$', alias="Reason")
    startdate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")
    enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Enddate")


class RetiredDefinition(BaseModel):
    """Model for retired person entries"""
    exist: ResetEnum
    kind: Optional[str] = Field(None, enum=[
        "PensionPrivateSector", "SurvivalPension", "PensionSelfEmployed", "pensionPublicSector"
    ], alias="Kind")
    date_retired: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="DateRetired")
    apply_collecting_2nd_pillar: Optional[ResetEnum] = None


class SportsPersonDefinition(BaseModel):
    """Model for sports person entries"""
    exist: ResetEnum
    recognized_foreign_sportsperson: Optional[ResetEnum] = None
    opportunity_contract: Optional[ResetEnum] = None


class StudentDefinition(BaseModel):
    """Model for student entries"""
    exist: ResetEnum
    solidarity_contribution: ResetEnum


class ContractModel(BaseModel):
    """Model for contract entries"""
    # Required fields
    startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Startdate")

    # Optional fields
    enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Enddate")
    employment_status: Optional[ContractTypeEnum] = None
    contract: Optional[str] = Field(None, enum=[
        "Usually", "FlexiVerbal", "FlexiWritten", "FlexiLiable", "Sportsperson",
        "Housekeeper", "Servant", "Agriculture", "Homework", "HomeworkChildcare",
        "Physician", "PhysicianTraining", "PhysicianIndependant", "ApprenticeFlemisch",
        "ApprenticeFrench", "ApprenticeGerman", "ApprenticeManager", "ApprenticeIndustrial",
        "ApprenticeSocio", "ApprenticeBio", "ApprenticeAlternating", "EarlyRetirement",
        "EarlyRetirementPartTime", "FreeNOSS", "FreeNOSSManager", "FreeNOSSOther",
        "FreeNOSSSportingEvent", "FreeNOSSHelper", "FreeNOSSSocio", "FreeNOSSEducation",
        "FreeNOSSSpecialCultures", "FreeNOSSVolunteer", "Horeca", "HorecaExtraHourLiable",
        "HorecaExtraDayLiable", "HorecaExtraHourForfait", "HorecaExtraDayForfait",
        "HorecaFlexiVerbal", "HorecaFlexiWritten", "HorecaFlexiLiable", "Construction",
        "ConstructionAlternating", "ConstructionApprenticeYounger", "ConstructionApprentice",
        "ConstructionGodfather", "JobTrainingIBO", "JobTrainingSchool", "JobTrainingVDAB",
        "JobTrainingLiberalProfession", "JobTrainingEntry", "JobTrainingPFIWa",
        "JobTrainingABO", "JobTrainingPFIBx", "JobTrainingBIO", "JobTrainingAlternating",
        "JobTrainingDisability", "NonProfitRiziv", "NonProfitGesco", "NonProfitDAC",
        "NonProfitPrime", "NonProfitLowSkilled", "Artist", "ArtistWithContract",
        "ArtistWithoutContract", "Transport", "TransportNonMobile", "TransportGarage",
        "Aircrew", "AircrewPilot", "AircrewCabinCrew", "Interim", "InterimTemporary",
        "InterimsPermanent", "External", "ExternalApplicant", "ExternalSubcontractor",
        "ExternalAgentIndependant", "ExternalExtern", "ExternalIntern", "ExternalLegalPerson",
        "SalesRepresentative", "SportsTrainer"
    ], alias="Contract")
    cat_rsz: Optional[str] = Field(None, min_length=3, max_length=3, pattern=r'^[0-9]*$', alias="CatRSZ")
    par_com: Optional[str] = Field(None, min_length=3, max_length=10, pattern=r'^[0-9. ]*$', alias="ParCom")
    document_c78: Optional[str] = Field(None, enum=[
        "Nihil", "C783", "C784", "C78Activa", "C78Start", "C78Sine", "C78ShortTerm",
        "WalloniaLongtermJobSeekers", "WalloniaYoungJobSeekers", "WalloniaImpulsionInsertion",
        "BrusselsLongtermJobSeekers", "BrusselsReducedAbility"
    ], alias="DocumentC78")
    code_c98: Optional[ResetEnum] = None
    code_c131a: Optional[ResetEnum] = None
    code_c131a_request_ft: Optional[ResetEnum] = None
    code_c131: Optional[ResetEnum] = None
    risk: Optional[str] = Field(None, min_length=0, max_length=10, alias="Risk")
    social_security_card: Optional[str] = Field(None, min_length=0, max_length=15, alias="SocialSecurityCard")
    work_permit: Optional[str] = Field(None, min_length=0, max_length=15, alias="WorkPermit")
    date_in_service: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="DateInService")
    seniority: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="Seniority")
    date_professional_experience: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="DateProfessionalExperience")
    scale_salary_seniority: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="ScaleSalarySeniority")
    start_probation_period: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="StartProbationPeriod")
    end_probation_period: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="EndProbationPeriod")
    fixed_term: Optional[ResetEnum] = None
    end_fixed_term: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="EndFixedTerm")
    date_out_service: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$', alias="DateOutService")
    reason_out: Optional[str] = None
    working_time: Optional[WorkingTimeEnum] = None
    spec_working_time: Optional[SpecWorkingTimeEnum] = None
    schedule: Optional[str] = Field(None, min_length=0, max_length=4, alias="Schedule")
    weekhours_worker: Optional[float] = Field(None, ge=1, le=50, alias="WeekhoursWorker")
    weekhours_employer: Optional[float] = Field(None, ge=1, le=50, alias="WeekhoursEmployer")
    weekhours_worker_average: Optional[float] = Field(None, ge=1, le=50, alias="WeekhoursWorkerAverage")
    weekhours_employer_average: Optional[float] = Field(None, ge=1, le=50, alias="WeekhoursEmployerAverage")
    weekhours_worker_effective: Optional[float] = Field(None, ge=1, le=50, alias="WeekhoursWorkerEffective")
    weekhours_employer_effective: Optional[float] = Field(None, ge=1, le=50, alias="WeekhoursEmployerEffective")
    days_week: Optional[float] = None
    days_week_ft: Optional[float] = None
    reducing_working_kind: Optional[str] = Field(None, enum=["Nihil", "Paid", "Unpaid"], alias="ReducingWorkingKind")
    reducing_working_kind_days: Optional[float] = None
    reducing_working_kind_hours: Optional[float] = None
    part_time_return_to_work: Optional[str] = Field(None, min_length=0, max_length=4, alias="PartTimeReturnTowork")
    asr_schedule: Optional[str] = Field(None, min_length=0, max_length=2, alias="ASRSchedule")
    proff_cat: Optional[str] = Field(None, min_length=0, max_length=10, alias="ProffCat")
    function: Optional[str] = Field(None, min_length=0, max_length=10, alias="Function")
    function_description: Optional[str] = Field(None, min_length=0, max_length=50, alias="FunctionDescription")
    social_balance_joblevel: Optional[str] = Field(None, enum=[
        "OperationalStaff", "ExecutiveStaff", "ManagementStaff", "ByFunction"
    ], alias="SocialBalanceJoblevel")
    office: Optional[int] = None
    division: Optional[str] = Field(None, min_length=0, max_length=10, alias="Division")
    invoicing_division: Optional[str] = Field(None, min_length=0, max_length=10, alias="InvoicingDivision")
    cost_centre: Optional[str] = Field(None, min_length=0, max_length=15, alias="CostCentre")
    scale_salary_prisma: Optional[ResetEnum] = None
    scale_salary_use: Optional[ResetEnum] = None
    scale_salary_definition: Optional[str] = Field(None, min_length=0, max_length=10, alias="ScaleSalaryDefinition")
    scale_salary_category: Optional[str] = Field(None, min_length=0, max_length=10, alias="ScaleSalaryCategory")
    scale_salary_scale: Optional[str] = Field(None, min_length=0, max_length=100, alias="ScaleSalaryScale")
    exclude_for_dmfa_declaration: Optional[ResetEnum] = None
    agriculture_type: Optional[AgricultureTypeEnum] = None
    no_dimona: Optional[ResetEnum] = None
    no_dmfa: Optional[ResetEnum] = None
    no_asrdrs: Optional[ResetEnum] = None
    security: Optional[str] = Field(None, min_length=0, max_length=10, alias="Security")

    # Nested models
    career_break: Optional[CareerBreakDefinition] = None
    certain_work: Optional[CertainWorkDefinition] = None
    dimona: Optional[ClsDimona] = None
    international_employment: Optional[InternationalEmploymentDefinition] = None
    method_of_remuneration: Optional[MethodOfRemunerationDefinition] = None
    progressive_work_resumption: Optional[ProgressiveWorkResumptionDefinition] = None
    protected_employee: Optional[ProtectedEmployeeDefinition] = None
    retired: Optional[RetiredDefinition] = None
    sportsperson: Optional[SportsPersonDefinition] = None
    student: Optional[StudentDefinition] = None
    salary_compositions: Optional[List[clsSalaryComposition]] = None
