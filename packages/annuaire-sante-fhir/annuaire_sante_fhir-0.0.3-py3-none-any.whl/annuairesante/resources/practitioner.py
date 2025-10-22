"""Practitioner resource."""

from .base import BaseResource


class PractitionerResource(BaseResource):
    """API wrapper for Practitioner resources (healthcare professionals).

    Available search parameters:
        _id (token): Technical resource ID
        _lastUpdated (date): Last update date (supports ge, le, gt, lt prefixes)
        active (token): Professional exercise status (true/false)
        data-information-system (token): Information system (RPPS, ADELI, etc.)
        family (string): Professional's family name (supports :contains, :exact)
        given (string): Professional's given name (supports :contains, :exact)
        identifier (token): Professional identifier (RPPS, IDNPS, ADELI)
        identifier-type (token): Type of identifier
        mailbox-mss (string): Secure Health Messaging mailbox
        name (string): Full name search (family + given)
        number-smartcard (string): Professional card number (CPS, CPF, etc.)
        qualification-code (token): Diploma, profession, or skill code

    Example:
        ```python
        # Search by name
        bundle = client.practitioner.search(family="MARTIN", given="Jean")

        # Search by RPPS identifier
        bundle = client.practitioner.search(identifier="10000123456")

        # Search active pharmacists
        bundle = client.practitioner.search(
            **{"qualification-code": "21"},  # Pharmacien
            active=True
        )

        # Incremental sync - only updated after date
        for pract in client.practitioner.search_all(
            _lastUpdated="ge2025-01-01T00:00:00Z"
        ):
            db.upsert(pract)
        ```
    """

    resource_type = "Practitioner"
