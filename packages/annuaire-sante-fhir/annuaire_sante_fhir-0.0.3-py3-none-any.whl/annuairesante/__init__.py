"""
Annuaire Sante - Client Python moderne pour l'API FHIR de l'Annuaire Sante.

Cette bibliotheque fournit:
- Des modeles Pydantic propres et DB-ready sans artefacts FHIR
- Des transformateurs FHIR vers JSON avec resolution automatique des codes MOS
- Un client HTTP pour interroger l'API Annuaire Sante
- Support complet des profils FR Core et AS DP (v1.1.0)
"""

__version__ = "0.0.3"

from .client import AnnuaireSanteClient
from .exceptions import (
    AnnuaireSanteError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TransformationError,
    ValidationError,
)
from .models import (
    Device,
    HealthcareService,
    Organization,
    Practitioner,
    PractitionerRole,
)
from .mos.resolver import MOSResolver
from .transformers import (
    transform_device,
    transform_healthcare_service,
    transform_organization,
    transform_practitioner,
    transform_practitioner_role,
)

__all__ = [
    # Version
    "__version__",
    # Client
    "AnnuaireSanteClient",
    # Models
    "Practitioner",
    "Organization",
    "PractitionerRole",
    "HealthcareService",
    "Device",
    # Transformers
    "transform_practitioner",
    "transform_organization",
    "transform_practitioner_role",
    "transform_healthcare_service",
    "transform_device",
    # MOS
    "MOSResolver",
    # Exceptions
    "AnnuaireSanteError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "TransformationError",
]
