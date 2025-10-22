"""Transformateur FHIR -> JSON pour HealthcareService."""

from typing import Any, Optional

from ..models.common import Coding
from ..models.healthcare_service import HealthcareService
from .base import BaseTransformer


class HealthcareServiceTransformer(BaseTransformer):
    """Transforme un HealthcareService FHIR en modele JSON propre."""

    def transform(self, fhir_data: dict[str, Any], include_raw: bool = False) -> HealthcareService:
        """
        Transforme les donnees FHIR en modele HealthcareService propre.

        Args:
            fhir_data: Dictionnaire JSON FHIR d'un HealthcareService
            include_raw: Si True, inclut les donnees FHIR brutes dans le champ fhir_raw

        Returns:
            Instance HealthcareService avec tous les codes MOS resolus
        """
        extensions = fhir_data.get("extension", [])

        # Extraire et indexer les codings
        categories_raw = self._extract_codings_list(fhir_data.get("category", []))
        types_raw = self._extract_codings_list(fhir_data.get("type", []))
        characteristics_raw = self._extract_codings_list(fhir_data.get("characteristic", []))
        eligibility_raw = self._extract_eligibility_codings(fhir_data.get("eligibility", []))

        return HealthcareService(
            identifiers=self.extract_identifiers(fhir_data.get("identifier", [])),
            name=fhir_data.get("name"),
            organization_id=self._extract_reference_id(fhir_data.get("providedBy", {})),
            authorization=self.extract_authorization(extensions),
            categories_by_name=self.index_codings_by_system_name(categories_raw),
            categories_raw=categories_raw,
            types_by_name=self.index_codings_by_system_name(types_raw),
            types_raw=types_raw,
            characteristics_by_name=self.index_codings_by_system_name(characteristics_raw),
            characteristics_raw=characteristics_raw,
            eligibility_by_name=self.index_codings_by_system_name(eligibility_raw),
            eligibility_raw=eligibility_raw,
            metadata=self.extract_metadata(fhir_data),
            active=fhir_data.get("active", True),
            fhir_raw=fhir_data if include_raw else None,
        )

    def _extract_reference_id(self, reference_data: dict[str, Any]) -> Optional[str]:
        """Extrait l'ID depuis une reference FHIR."""
        ref_raw = reference_data.get("reference", "")
        ref = str(ref_raw) if ref_raw else ""
        if "/" in ref:
            return ref.split("/")[-1]
        return ref if ref else None

    def _extract_codings_list(self, codeable_concepts: list[dict[str, Any]]) -> list[Coding]:
        """Extrait et resout une liste de CodeableConcepts."""
        result = []
        for concept in codeable_concepts:
            codings = concept.get("coding", [])
            for coding in codings:
                resolved = self.resolve_coding(coding)
                result.append(resolved)
        return result

    def _extract_eligibility_codings(self, eligibility_list: list[dict[str, Any]]) -> list[Coding]:
        """Extrait et resout les codings d'eligibilite/clientele."""
        result = []
        for eligibility in eligibility_list:
            # eligibility contient un champ "code" qui est un CodeableConcept
            code_concept = eligibility.get("code", {})
            codings = code_concept.get("coding", [])
            for coding in codings:
                resolved = self.resolve_coding(coding)
                result.append(resolved)
        return result


def transform_healthcare_service(
    fhir_data: dict[str, Any], include_raw: bool = False
) -> HealthcareService:
    """
    Fonction utilitaire pour transformer un HealthcareService FHIR.

    Args:
        fhir_data: Dictionnaire JSON FHIR d'un HealthcareService
        include_raw: Si True, inclut les donnees FHIR brutes dans le champ fhir_raw

    Returns:
        Instance HealthcareService avec donnees normalisees
    """
    transformer = HealthcareServiceTransformer()
    return transformer.transform(fhir_data, include_raw=include_raw)
