"""Transformateur FHIR -> JSON pour PractitionerRole."""

from typing import Any, Optional

from ..models.practitioner_role import PractitionerRole
from .base import BaseTransformer


class PractitionerRoleTransformer(BaseTransformer):
    """Transforme un PractitionerRole FHIR en modele JSON propre."""

    def transform(self, fhir_data: dict[str, Any], include_raw: bool = False) -> PractitionerRole:
        """
        Transforme les donnees FHIR en modele PractitionerRole propre.

        Args:
            fhir_data: Dictionnaire JSON FHIR d'un PractitionerRole
            include_raw: Si True, inclut les donnees FHIR brutes dans le champ fhir_raw

        Returns:
            Instance PractitionerRole avec tous les codes MOS resolus
        """
        # Extraire les codes
        codes_by_name, codes_raw = self._extract_codes(fhir_data)

        return PractitionerRole(
            practitioner_id=self._extract_reference_id(fhir_data.get("practitioner", {})),
            organization_id=self._extract_reference_id(fhir_data.get("organization", {})),
            identifiers=self.extract_identifiers(fhir_data.get("identifier", [])),
            codes_by_name=codes_by_name,
            codes_raw=codes_raw,
            period=self.extract_period(fhir_data.get("period")),
            contacts=self.extract_contact_info(fhir_data.get("telecom", [])),
            metadata=self.extract_metadata(fhir_data),
            active=fhir_data.get("active", True),
            fhir_raw=fhir_data if include_raw else None,
        )

    def _extract_reference_id(self, reference_data: dict[str, Any]) -> Optional[str]:
        """Extrait l'ID depuis une reference FHIR."""
        ref_raw = reference_data.get("reference", "")
        ref = str(ref_raw) if ref_raw else ""
        # Format: "Practitioner/003-3014698-3057235" -> "003-3014698-3057235"
        if "/" in ref:
            return ref.split("/")[-1]
        return ref if ref else None

    def _extract_codes(self, fhir_data: dict[str, Any]) -> tuple[Any, Any]:
        """
        Extrait et resout les codes de role/exercice.

        Returns:
            Tuple: (codes_by_name, codes_raw)
        """
        codes_raw = []
        code_data_list = fhir_data.get("code", [])

        for code_data in code_data_list:
            codings = code_data.get("coding", [])
            for coding in codings:
                resolved = self.resolve_coding(coding)
                codes_raw.append(resolved)

        # Indexer par nom de systeme
        codes_by_name = self.index_codings_by_system_name(codes_raw)

        return codes_by_name, codes_raw


def transform_practitioner_role(
    fhir_data: dict[str, Any], include_raw: bool = False
) -> PractitionerRole:
    """
    Fonction utilitaire pour transformer un PractitionerRole FHIR.

    Args:
        fhir_data: Dictionnaire JSON FHIR d'un PractitionerRole
        include_raw: Si True, inclut les donnees FHIR brutes dans le champ fhir_raw

    Returns:
        Instance PractitionerRole avec donnees normalisees
    """
    transformer = PractitionerRoleTransformer()
    return transformer.transform(fhir_data, include_raw=include_raw)
