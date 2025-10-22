"""Transformateur FHIR -> JSON pour Organization."""

from typing import Any, Optional

from ..models.common import OrganizationType
from ..models.organization import Organization, OrganizationIdentifiers
from .base import BaseTransformer


class OrganizationTransformer(BaseTransformer):
    """Transforme une Organization FHIR en modele JSON propre."""

    def transform(self, fhir_data: dict[str, Any], include_raw: bool = False) -> Organization:
        """
        Transforme les donnees FHIR en modele Organization propre.

        Args:
            fhir_data: Dictionnaire JSON FHIR d'une Organization
            include_raw: Si True, inclut les donnees FHIR brutes dans le champ fhir_raw

        Returns:
            Instance Organization avec tous les codes MOS resolus
        """
        extensions = fhir_data.get("extension", [])

        # Extraire les types
        types_by_category, primary_type, types_raw = self._extract_types(fhir_data)

        return Organization(
            identifiers=self._extract_identifiers(fhir_data),
            name=fhir_data.get("name"),
            aliases=fhir_data.get("alias", []),
            short_name=self._extract_short_name(extensions),
            description=self._extract_description(extensions),
            types_by_category=types_by_category,
            primary_type=primary_type,
            types_raw=types_raw,
            period=self._extract_organization_period(extensions),
            pharmacy_licence=self._extract_pharmacy_licence(extensions),
            pricing_model=None,  # Extension a documenter si presente
            budget_type=None,  # Extension a documenter si presente
            closing_type=None,  # Extension a documenter si presente
            authorization_deadline=None,  # Extension a documenter si presente
            addresses=[self.extract_address(addr) for addr in fhir_data.get("address", [])],
            contacts=self.extract_contact_info(fhir_data.get("telecom", [])),
            parent_organization_id=self._extract_parent_id(fhir_data),
            metadata=self.extract_metadata(fhir_data),
            active=fhir_data.get("active", True),
            fhir_raw=fhir_data if include_raw else None,
        )

    def _extract_identifiers(self, fhir_data: dict[str, Any]) -> OrganizationIdentifiers:
        """Extrait les identifiants avec slicing AS DP."""
        identifiers = fhir_data.get("identifier", [])

        idnst = None
        finej = None
        fineg = None
        siren = None
        siret = None
        adeli_rang = None
        rpps_rang = None
        internal_id = None

        for id_data in identifiers:
            system = id_data.get("system", "")
            value = id_data.get("value")
            type_obj = id_data.get("type", {})
            type_code = None

            codings = type_obj.get("coding", [])
            if codings:
                type_code = codings[0].get("code")

            # Identifier par type
            if type_code == "IDNST":
                idnst = value
            elif type_code == "FINEJ":
                finej = value
            elif type_code == "FINEG":
                fineg = value
            elif type_code == "FINESS":
                # Type générique FINESS - considérer comme FINEG par défaut
                if not fineg:
                    fineg = value
            elif type_code == "SIREN":
                siren = value
            elif type_code == "SIRET":
                siret = value
            elif "adeli" in system.lower() and "rang" in system.lower():
                adeli_rang = value
            elif "rpps" in system.lower() and "rang" in system.lower():
                rpps_rang = value
            elif type_code == "INTRN":
                internal_id = value

        # FINESS prioritaire: FINEJ puis FINEG
        finess = finej or fineg

        return OrganizationIdentifiers(
            idnst=idnst,
            finess=finess,
            finej=finej,
            fineg=fineg,
            siren=siren,
            siret=siret,
            adeli_rang=adeli_rang,
            rpps_rang=rpps_rang,
            internal_id=internal_id,
        )

    def _extract_short_name(self, extensions: list[dict[str, Any]]) -> Optional[str]:
        """Extrait le nom court."""
        for ext in extensions:
            if "short-name" in ext.get("url", ""):
                value: Any = ext.get("valueString")
                return str(value) if value is not None else None
        return None

    def _extract_description(self, extensions: list[dict[str, Any]]) -> Optional[str]:
        """Extrait la description."""
        for ext in extensions:
            if "description" in ext.get("url", "") and "short" not in ext.get("url", ""):
                value: Any = ext.get("valueString")
                return str(value) if value is not None else None
        return None

    def _extract_organization_period(self, extensions: list[dict[str, Any]]) -> Any:
        """Extrait la periode d'activite (organization-period)."""
        for ext in extensions:
            if "organization-period" in ext.get("url", ""):
                return self.extract_period(ext.get("valuePeriod"))
        return None

    def _extract_pharmacy_licence(self, extensions: list[dict[str, Any]]) -> Optional[str]:
        """Extrait le numero de licence de pharmacie."""
        for ext in extensions:
            if "pharmacy-licence" in ext.get("url", ""):
                value: Any = ext.get("valueString")
                return str(value) if value is not None else None
        return None

    def _extract_types(
        self, fhir_data: dict[str, Any]
    ) -> tuple[dict[str, Any], Optional[OrganizationType], list[OrganizationType]]:
        """
        Extrait les types d'organisation multidimensionnels.

        Returns:
            Tuple: (types_by_category, primary_type, types_raw)
            - types_by_category: dict[str, OrganizationType|list[OrganizationType]]
            - primary_type: OrganizationType (celui sans categorie)
            - types_raw: list[OrganizationType]
        """
        types_raw: list[OrganizationType] = []
        types_by_category: dict[str, Any] = {}
        primary_type: Optional[OrganizationType] = None

        type_data_list = fhir_data.get("type", [])

        for type_data in type_data_list:
            # Recuperer la categorie depuis l'extension organization-type-category
            category = None
            extensions = type_data.get("extension", [])
            for ext in extensions:
                if "organization-type-category" in ext.get("url", ""):
                    category = ext.get("valueString") or ext.get("valueCode")

            # Resoudre le code
            codings = type_data.get("coding", [])
            if codings:
                coding_data = codings[0]
                coding = self.resolve_coding(coding_data)

                # Si pas de categorie depuis extension, deduire depuis le systeme
                if not category and coding_data.get("system"):
                    system_name = self.mos_resolver.get_system_name(coding_data["system"])
                    if system_name:
                        category = system_name

                org_type = OrganizationType(
                    code=coding.code,
                    display=coding.display,
                    category=category,
                )

                # Ajouter a la liste raw
                types_raw.append(org_type)

                # Indexer par categorie
                if category:
                    # Verifier si cette categorie existe deja
                    if category in types_by_category:
                        # Convertir en liste si necessaire
                        existing = types_by_category[category]
                        if isinstance(existing, list):
                            existing.append(org_type)
                        else:
                            types_by_category[category] = [existing, org_type]
                    else:
                        # Premiere occurrence
                        types_by_category[category] = org_type
                else:
                    # Type sans categorie = type principal
                    primary_type = org_type

        return types_by_category, primary_type, types_raw

    def _extract_parent_id(self, fhir_data: dict[str, Any]) -> Optional[str]:
        """Extrait l'ID de l'organisation parente."""
        part_of = fhir_data.get("partOf", {})
        ref: Any = part_of.get("reference")
        if ref:
            # Format: "Organization/001-02-1362138" -> "001-02-1362138"
            return str(ref).split("/")[-1]
        return None


def transform_organization(fhir_data: dict[str, Any], include_raw: bool = False) -> Organization:
    """
    Fonction utilitaire pour transformer une Organization FHIR.

    Args:
        fhir_data: Dictionnaire JSON FHIR d'une Organization
        include_raw: Si True, inclut les donnees FHIR brutes dans le champ fhir_raw

    Returns:
        Instance Organization avec donnees normalisees
    """
    transformer = OrganizationTransformer()
    return transformer.transform(fhir_data, include_raw=include_raw)
