"""HealthcareService resource."""

from .base import BaseResource


class HealthcareServiceResource(BaseResource):
    """API wrapper for HealthcareService resources (healthcare activities/services).

    Available search parameters:
        _id (token): Technical resource ID
        _lastUpdated (date): Last update date (supports ge, le, gt, lt prefixes)
        _profile (uri): Healthcare Service profile selector
        active (token): Active service (true/false)
        as_sp_data-information-system (token): Information system
        characteristic (token): Activity type or form (TRE_R276-FormeActivite)
        identifier (token): Service identifier
        organization (reference): Attached organization technical ID
        service-category (token): Healthcare activity modality (TRE_R275-ModaliteActivite)
        service-type (token): Discipline or regulated health activity (TRE_R274, TRE_R277)

    Example:
        ```python
        # Search services for an organization
        bundle = client.healthcare_service.search(
            organization="001-01-174986"
        )

        # Search by service category (modality)
        bundle = client.healthcare_service.search(
            **{"service-category": "https://mos.esante.gouv.fr/NOS/TRE_R275-ModaliteActivite/FHIR/TRE-R275-ModaliteActivite|20"}
        )

        # Search active services
        bundle = client.healthcare_service.search(active=True)

        # Sync all services
        for service in client.healthcare_service.search_all():
            db.save(service)
        ```
    """

    resource_type = "HealthcareService"
