"""Transformateur FHIR -> JSON pour Practitioner."""

from typing import Any

from ..models.common import Qualification
from ..models.practitioner import (
    Communication,
    Practitioner,
    PractitionerIdentifiers,
    PractitionerName,
)
from .base import BaseTransformer


class PractitionerTransformer(BaseTransformer):
    """Transforme un Practitioner FHIR en modele JSON propre."""

    def transform(self, fhir_data: dict[str, Any], include_raw: bool = False) -> Practitioner:
        """
        Transforme les donnees FHIR en modele Practitioner propre.

        Args:
            fhir_data: Dictionnaire JSON FHIR d'un Practitioner
            include_raw: Si True, inclut les donnees FHIR brutes dans le champ fhir_raw

        Returns:
            Instance Practitioner avec tous les codes MOS resolus
        """
        # Extraire les qualifications
        qualifications_dict, qualifications_raw = self._extract_qualifications(fhir_data)

        return Practitioner(
            identifiers=self._extract_identifiers(fhir_data),
            name=self._extract_name(fhir_data),
            gender=fhir_data.get("gender"),
            birth_date=fhir_data.get("birthDate"),
            deceased=fhir_data.get("deceasedBoolean", False)
            or fhir_data.get("deceasedDateTime") is not None,
            deceased_date=fhir_data.get("deceasedDateTime"),
            contacts=self.extract_contact_info(fhir_data.get("telecom", [])),
            addresses=[self.extract_address(addr) for addr in fhir_data.get("address", [])],
            qualifications=qualifications_dict,
            qualifications_raw=qualifications_raw,
            smartcards=self.extract_smartcards(fhir_data.get("extension", [])),
            communications=self._extract_communications(fhir_data),
            metadata=self.extract_metadata(fhir_data),
            active=fhir_data.get("active", True),
            fhir_raw=fhir_data if include_raw else None,
        )

    def _extract_identifiers(self, fhir_data: dict[str, Any]) -> PractitionerIdentifiers:
        """Extrait les identifiants avec slicing AS DP."""
        identifiers = fhir_data.get("identifier", [])

        idnps = None
        rpps = None
        adeli = None

        for id_data in identifiers:
            system = id_data.get("system", "")
            value = id_data.get("value")
            type_obj = id_data.get("type", {})
            type_code = None

            codings = type_obj.get("coding", [])
            if codings:
                type_code = codings[0].get("code")

            # Identifier par type
            if type_code == "IDNPS":
                idnps = value
            elif type_code == "RPPS" or "rpps" in system.lower():
                rpps = value
            elif type_code == "ADELI" or "adeli" in system.lower():
                adeli = value

        if not idnps:
            raise ValueError("IDNPS obligatoire manquant")
        if not rpps:
            raise ValueError("RPPS obligatoire manquant")

        return PractitionerIdentifiers(idnps=idnps, rpps=rpps, adeli=adeli)

    def _extract_name(self, fhir_data: dict[str, Any]) -> PractitionerName:
        """Extrait le nom FR Core HumanName."""
        names = fhir_data.get("name", [])
        if not names:
            return PractitionerName()

        name_data = names[0]  # Premier nom

        # Civilite (prefix) - 0..1
        prefix_list = name_data.get("prefix", [])
        prefix = prefix_list[0] if prefix_list else None

        # Suffixes (titres d'exercice) - 0..*
        suffix_list = name_data.get("suffix", [])

        # Assembly order depuis extension
        assembly_order = None
        extensions = name_data.get("extension", [])
        for ext in extensions:
            if "assemblyOrder" in ext.get("url", ""):
                assembly_order = ext.get("valueCode")

        return PractitionerName(
            family=name_data.get("family"),
            given=name_data.get("given", []),
            prefix=prefix,
            suffix=suffix_list,
            full_text=name_data.get("text"),
            assembly_order=assembly_order,
        )

    def _extract_qualifications(
        self, fhir_data: dict[str, Any]
    ) -> tuple[dict[str, Any], list[Any]]:
        """
        Extrait les qualifications avec resolution MOS.

        Returns:
            Tuple: (qualifications_dict, qualifications_raw)
            - qualifications_dict: dict[str, dict[str, Coding|list[Coding]]]
            - qualifications_raw: list[Qualification]
        """
        qualifications_raw = []
        qualifications_dict: dict[str, Any] = {}

        qual_data_list = fhir_data.get("qualification", [])

        for qual_data in qual_data_list:
            code_obj = qual_data.get("code", {})
            codings = code_obj.get("coding", [])

            # Resoudre tous les codings
            resolved_codings = [self.resolve_coding(coding) for coding in codings]

            # Determiner le type
            qual_type = "unknown"
            for coding in resolved_codings:
                system = coding.system or ""
                if "TRE_R48-DiplomeEtatFrancais" in system or "TRE_R14-TypeDiplome" in system:
                    qual_type = "diplome"
                    break
                elif (
                    "TRE_G15-ProfessionSante" in system
                    or "TRE_R09-CategorieProfessionnelle" in system
                ):
                    qual_type = "profession"
                    break

            # Period
            period = self.extract_period(qual_data.get("period"))

            # Issuer
            issuer_obj = qual_data.get("issuer", {})
            issuer = issuer_obj.get("display") or issuer_obj.get("reference")

            # Ajouter a la liste raw
            qualifications_raw.append(
                Qualification(
                    type=qual_type,
                    codes=resolved_codings,
                    period=period,
                    issuer=issuer,
                )
            )

            # Construire le dictionnaire indexe par nom de systeme
            if qual_type not in qualifications_dict:
                qualifications_dict[qual_type] = {}

            # Utiliser la methode helper pour indexer les codings
            indexed_codings = self.index_codings_by_system_name(resolved_codings)
            qualifications_dict[qual_type].update(indexed_codings)

        return qualifications_dict, qualifications_raw

    def _extract_communications(self, fhir_data: dict[str, Any]) -> list[Communication]:
        """Extrait les langues de communication."""
        communications = []
        comm_data_list = fhir_data.get("communication", [])

        for comm_data in comm_data_list:
            language = comm_data.get("language", {})
            codings = language.get("coding", [])

            if codings:
                coding = codings[0]
                code = coding.get("code")
                display = coding.get("display")

                # Resoudre avec MOS si necessaire
                if not display:
                    system = coding.get("system")
                    if system and code:
                        display = self.mos_resolver.resolve(system, code)

                communications.append(Communication(code=code, display=display))

        return communications


def transform_practitioner(fhir_data: dict[str, Any], include_raw: bool = False) -> Practitioner:
    """
    Fonction utilitaire pour transformer un Practitioner FHIR.

    Args:
        fhir_data: Dictionnaire JSON FHIR d'un Practitioner
        include_raw: Si True, inclut les donnees FHIR brutes dans le champ fhir_raw

    Returns:
        Instance Practitioner avec donnees normalisees
    """
    transformer = PractitionerTransformer()
    return transformer.transform(fhir_data, include_raw=include_raw)
