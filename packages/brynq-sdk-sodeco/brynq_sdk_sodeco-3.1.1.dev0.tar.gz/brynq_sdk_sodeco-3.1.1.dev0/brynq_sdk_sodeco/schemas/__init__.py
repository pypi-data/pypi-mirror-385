"""Schema definitions for Sodeco package"""

DATEFORMAT = '%Y%m%d'

# Worker schemas
from .worker import (
    # GET schemas (Pandera - for DataFrame validation)
    EmployeeGet,
    FamilyGet,
    AddressGet,
    CommunicationGet,
    ContractGet,
    TaxGet,
    ReplacementGet,
    SalaryCompositionGet,
    # POST/PUT schemas (Pydantic - for request validation)
    WorkerCreate,
    WorkerUpdate
)

# Other schemas
from .absence import AbsenceSchema, AbsencesSchema
from .absencenote import AbsenceNoteSchema
from .address import AddressSchema
from .car import CarSchema
from .communication import CommunicationSchema
from .contract import ContractModel
from .costcentre import CostCentreSchema
from .dimona import PostDimonaSchema, GetDimonaSchema, UsingDataSchema
from .divergentpayment import DivergentPaymentSchema
from .family import FamilySchema
from .replacement import ReplacementSchema
from .salarycomposition import SalaryCompositionSchema
from .schedule import ScheduleSchema
from .tax import TaxSchema

__all__ = [
    'DATEFORMAT',
    # Worker schemas
    'EmployeeGet',
    'FamilyGet',
    'AddressGet',
    'CommunicationGet',
    'ContractGet',
    'TaxGet',
    'ReplacementGet',
    'SalaryCompositionGet',
    'WorkerCreate',
    'WorkerUpdate',
    # Other schemas
    'AbsenceSchema',
    'AbsencesSchema',
    'AbsenceNoteSchema',
    'AddressSchema',
    'CarSchema',
    'CommunicationSchema',
    'ContractModel',
    'CostCentreSchema',
    'PostDimonaSchema',
    'GetDimonaSchema',
    'UsingDataSchema',
    'DivergentPaymentSchema',
    'FamilySchema',
    'ReplacementSchema',
    'SalaryCompositionSchema',
    'ScheduleSchema',
    'TaxSchema'
]
