"""PractitionerRole resource."""

from .base import BaseResource


class PractitionerRoleResource(BaseResource):
    """API wrapper for PractitionerRole resources (professional exercise situations).

    Available search parameters:
        _id (token): Technical resource ID
        _lastUpdated (date): Last update date (supports ge, le, gt, lt prefixes)
        active (token): Active exercise situation (true/false)
        data-information-system (token): Information system
        data-registration-authority (token): Registration authority
        identifier (token): Professional activity identifier
        mailbox-mss (string): Secure Health Messaging mailbox
        organization (reference): Organization technical ID
        practitioner (reference): Practitioner technical ID
        role (token): Function, activity type, exercise mode, or section code

    Example:
        ```python
        # Search roles for a specific practitioner
        bundle = client.practitioner_role.search(
            practitioner="003-123456"
        )

        # Search roles in a specific organization
        bundle = client.practitioner_role.search(
            organization="001-01-879996"
        )

        # Search by role (activity type)
        bundle = client.practitioner_role.search(
            role="https://mos.esante.gouv.fr/NOS/TRE_R22-GenreActivite/FHIR/TRE-R22-GenreActivite|204"
        )

        # Sync all active roles
        for role in client.practitioner_role.search_all(active=True):
            db.save(role)
        ```
    """

    resource_type = "PractitionerRole"
