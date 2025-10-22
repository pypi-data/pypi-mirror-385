"""Device resource."""

from .base import BaseResource


class DeviceResource(BaseResource):
    """API wrapper for Device resources (heavy medical equipment).

    Available search parameters:
        _id (token): Technical resource ID
        _lastUpdated (date): Last update date (supports ge, le, gt, lt prefixes)
        data-information-system (token): Information system
        identifier (token): ARHGOS equipment number
        manufacturer (string): Equipment brand/manufacturer
        model (string): Equipment model
        organization (reference): Associated organization technical ID
        status (token): Equipment status (active, inactive, entered-in-error, unknown)
        type (token): Heavy medical equipment type (TRE_R272-EquipementMaterielLourd)

    Example:
        ```python
        # Search devices for an organization
        bundle = client.device.search(
            organization="001-01-1272801"
        )

        # Search by equipment type (scanners)
        bundle = client.device.search(
            type="https://mos.esante.gouv.fr/NOS/TRE_R272-EquipementMaterielLourd/FHIR/TRE-R272-EquipementMaterielLourd|05602"
        )

        # Search active devices
        bundle = client.device.search(status="active")

        # Search by ARHGOS identifier
        bundle = client.device.search(identifier="93-93-67204")

        # Sync all devices
        for device in client.device.search_all():
            db.save(device)
        ```
    """

    resource_type = "Device"
