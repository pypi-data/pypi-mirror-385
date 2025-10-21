from pandera import Field
from typing import Optional
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class CommunicationSchema(BrynQPanderaDataFrameModel):
    # Required fields
    communication_type: str = Field(nullable=False, isin=[
        'None', 'Phone', 'GSM', 'Email', 'PrivatePhone', 'Fax',
        'InternalPhone', 'PrivateEmail', 'GSMEntreprise', 'Website'
    ], alias="CommunicationType")
    value: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 100}, alias="Value")

    # Optional fields
    id: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 100}, alias="ID")
    contact_person: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 100}, alias="ContactPerson")
    contact_person_firstname: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 50}, alias="ContactPersonFirstname")
