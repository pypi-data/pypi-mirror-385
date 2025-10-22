"""Modeles de donnees DB-ready pour l'Annuaire Sante."""

from .common import (
    Address,
    Authorization,
    Coding,
    ContactInfo,
    DataTrace,
    Identifier,
    Metadata,
    MSSanteMailbox,
    OrganizationType,
    Period,
    Qualification,
    Smartcard,
)
from .device import Device
from .healthcare_service import HealthcareService
from .organization import Organization, OrganizationIdentifiers
from .practitioner import (
    Communication,
    Practitioner,
    PractitionerIdentifiers,
    PractitionerName,
)
from .practitioner_role import PractitionerRole

__all__ = [
    # Common
    "Address",
    "Authorization",
    "Coding",
    "Communication",
    "ContactInfo",
    "DataTrace",
    "Identifier",
    "Metadata",
    "MSSanteMailbox",
    "OrganizationType",
    "Period",
    "Qualification",
    "Smartcard",
    # Resources
    "Device",
    "HealthcareService",
    "Organization",
    "OrganizationIdentifiers",
    "Practitioner",
    "PractitionerIdentifiers",
    "PractitionerName",
    "PractitionerRole",
]
