"""Transformateur FHIR -> JSON pour Device."""

from typing import Any, Optional

from ..models.device import Device
from .base import BaseTransformer


class DeviceTransformer(BaseTransformer):
    """Transforme un Device FHIR en modele JSON propre."""

    def transform(self, fhir_data: dict[str, Any], include_raw: bool = False) -> Device:
        """
        Transforme les donnees FHIR en modele Device propre.

        Args:
            fhir_data: Dictionnaire JSON FHIR d'un Device
            include_raw: Si True, inclut les donnees FHIR brutes dans le champ fhir_raw

        Returns:
            Instance Device avec tous les codes MOS resolus
        """
        extensions = fhir_data.get("extension", [])

        # Type d'equipement
        device_type = None
        type_data = fhir_data.get("type")
        if type_data:
            codings = type_data.get("coding", [])
            if codings:
                device_type = self.resolve_coding(codings[0])

        return Device(
            identifiers=self.extract_identifiers(fhir_data.get("identifier", [])),
            status=fhir_data.get("status", "unknown"),
            manufacturer=fhir_data.get("manufacturer"),
            device_type=device_type,
            owner_organization_id=self._extract_reference_id(fhir_data.get("owner", {})),
            authorization=self.extract_authorization(extensions),
            metadata=self.extract_metadata(fhir_data),
            fhir_raw=fhir_data if include_raw else None,
        )

    def _extract_reference_id(self, reference_data: dict[str, Any]) -> Optional[str]:
        """Extrait l'ID depuis une reference FHIR."""
        ref_raw = reference_data.get("reference", "")
        ref = str(ref_raw) if ref_raw else ""
        if "/" in ref:
            return ref.split("/")[-1]
        return ref if ref else None


def transform_device(fhir_data: dict[str, Any], include_raw: bool = False) -> Device:
    """
    Fonction utilitaire pour transformer un Device FHIR.

    Args:
        fhir_data: Dictionnaire JSON FHIR d'un Device
        include_raw: Si True, inclut les donnees FHIR brutes dans le champ fhir_raw

    Returns:
        Instance Device avec donnees normalisees
    """
    transformer = DeviceTransformer()
    return transformer.transform(fhir_data, include_raw=include_raw)
