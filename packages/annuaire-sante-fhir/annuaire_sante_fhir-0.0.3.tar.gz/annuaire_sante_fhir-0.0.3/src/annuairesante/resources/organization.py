"""Organization resource."""

from .base import BaseResource


class OrganizationResource(BaseResource):
    """API wrapper for Organization resources (healthcare structures).

    Available search parameters:
        _id (token): Technical resource ID
        _lastUpdated (date): Last update date (supports ge, le, gt, lt prefixes)
        active (token): Organization status (true/false)
        address (string): Full address search
        address-city (string): City name (use hyphens for multi-word cities)
        address-postalcode (string): Postal code
        data-information-system (token): Information system (FINESS, RPPS, etc.)
        identifier (token): Structure identifier (FINESS, SIRET, IDNST, etc.)
        identifier-type (token): Type of identifier
        mailbox-mss (string): Secure Health Messaging mailboxes
        name (string): Organization name (supports :contains, :exact)
        partof (reference): Geographic establishments linked to legal entity
        pharmacy-licence (string): Pharmacy license number
        type (token): Structure type, APE code, legal category, activity sector

    Example:
        ```python
        # Search pharmacies in Paris
        bundle = client.organization.search(
            type="620",  # Pharmacie d'officine
            **{"address-city": "Paris"}
        )

        # Search by FINESS identifier
        bundle = client.organization.search(identifier="750010753")

        # Search by name
        bundle = client.organization.search(name="hopital saint-louis")

        # Search active healthcare centers
        bundle = client.organization.search(
            type="603",  # Centre de sante
            active=True
        )

        # Incremental sync
        for org in client.organization.search_all(
            _lastUpdated="ge2025-01-01T00:00:00Z",
            **{"address-postalcode": "69"}  # Rhone department
        ):
            db.upsert(org)
        ```
    """

    resource_type = "Organization"
