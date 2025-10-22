"""Resource wrappers for Annuaire Sante API."""

from .device import DeviceResource
from .healthcare_service import HealthcareServiceResource
from .organization import OrganizationResource
from .practitioner import PractitionerResource
from .practitioner_role import PractitionerRoleResource

__all__ = [
    "PractitionerResource",
    "OrganizationResource",
    "PractitionerRoleResource",
    "HealthcareServiceResource",
    "DeviceResource",
]
