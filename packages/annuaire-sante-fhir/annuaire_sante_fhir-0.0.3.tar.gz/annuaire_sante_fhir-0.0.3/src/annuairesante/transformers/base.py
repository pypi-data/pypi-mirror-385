"""Transformations de base communes a toutes les ressources FHIR."""

from datetime import date
from typing import Any, Optional, Union

from ..models.common import (
    Address,
    Authorization,
    Coding,
    ContactInfo,
    DataTrace,
    Identifier,
    Metadata,
    MSSanteMailbox,
    Period,
    Smartcard,
)
from ..mos.resolver import MOSResolver, get_resolver


class BaseTransformer:
    """Transformateur de base avec methodes communes."""

    def __init__(self, mos_resolver: Optional[MOSResolver] = None):
        """
        Args:
            mos_resolver: Resolveur MOS optionnel. Si None, le singleton global sera utilise.
        """
        self.mos_resolver = mos_resolver or get_resolver()

    def extract_metadata(self, fhir_data: dict[str, Any]) -> Metadata:
        """Extrait les metadonnees FHIR."""
        meta = fhir_data.get("meta", {})

        # Extraire data-trace depuis meta.extension
        data_trace = None
        meta_extensions = meta.get("extension", [])
        for ext in meta_extensions:
            if "data-trace" in ext.get("url", ""):
                data_trace = self._extract_data_trace(ext)
                break

        return Metadata(
            id=fhir_data.get("id", ""),
            version_id=meta.get("versionId"),
            last_updated=meta.get("lastUpdated"),
            source=meta.get("source"),
            profiles=meta.get("profile", []),
            language=fhir_data.get("language"),
            data_trace=data_trace,
        )

    def _extract_data_trace(self, extension_data: dict[str, Any]) -> DataTrace:
        """Extrait les informations de tracabilite."""
        sub_extensions = extension_data.get("extension", [])

        autorite = None
        systeme = None
        date_maj = None

        for sub_ext in sub_extensions:
            url = sub_ext.get("url", "")
            if url == "autorite-enregistrement":
                # Peut etre un CodeableConcept
                concept = sub_ext.get("valueCodeableConcept", {})
                codings = concept.get("coding", [])
                if codings:
                    autorite = codings[0].get("code")
            elif url == "systeme-information":
                systeme = sub_ext.get("valueCode")
            elif url == "date-maj-ae":
                date_maj = sub_ext.get("valueDate")

        return DataTrace(
            autorite_enregistrement=autorite,
            systeme_information=systeme,
            date_maj_ae=date_maj,
        )

    def extract_period(self, period_data: Optional[dict[str, Any]]) -> Optional[Period]:
        """Extrait une periode."""
        if not period_data:
            return None

        return Period(start=period_data.get("start"), end=period_data.get("end"))

    def resolve_coding(self, coding_data: dict[str, Any]) -> Coding:
        """Resout un coding FHIR avec MOS."""
        system = coding_data.get("system")
        code = coding_data.get("code")
        display = coding_data.get("display")

        # Resoudre avec MOS si display absent
        if not display and system and code:
            display = self.mos_resolver.resolve(system, code)

        return Coding(system=system, code=code, display=display)

    def index_codings_by_system_name(
        self, codings: list[Coding]
    ) -> dict[str, Union[Coding, list[Coding]]]:
        """
        Indexe une liste de Codings par leur nom de systeme MOS lisible.

        Si le nom lisible n'est pas disponible (index MOS ancien format),
        utilise le code de table comme fallback (ex: "TRE-R48").

        Args:
            codings: Liste de Coding a indexer

        Returns:
            Dictionnaire {nom_systeme: Coding ou list[Coding]}
        """
        indexed: dict[str, Union[Coding, list[Coding]]] = {}

        for coding in codings:
            # Obtenir le nom lisible du systeme
            system_key = None
            if coding.system:
                system_key = self.mos_resolver.get_system_name(coding.system)

                # Fallback: si pas de nom lisible, extraire le code de table (TRE-R48)
                if not system_key:
                    system_key = self.mos_resolver._extract_table_name(coding.system)

            if system_key:
                # Verifier si ce systeme existe deja
                if system_key in indexed:
                    # Convertir en liste si necessaire
                    existing = indexed[system_key]
                    if isinstance(existing, list):
                        existing.append(coding)
                    else:
                        # Créer une nouvelle liste avec les deux éléments
                        new_list: list[Coding] = [existing, coding]  # type: ignore[list-item]
                        indexed[system_key] = new_list
                else:
                    # Premiere occurrence
                    indexed[system_key] = coding

        return indexed

    def extract_identifiers(self, identifiers_data: list[dict[str, Any]]) -> list[Identifier]:
        """Extrait la liste des identifiants."""
        result = []
        for id_data in identifiers_data:
            type_obj = id_data.get("type", {})
            type_code = None
            if type_obj:
                codings = type_obj.get("coding", [])
                if codings:
                    type_code = codings[0].get("code")

            result.append(
                Identifier(
                    system=id_data.get("system"),
                    value=id_data.get("value"),
                    type=type_code,
                    use=id_data.get("use"),
                )
            )
        return result

    def extract_address(self, address_data: dict[str, Any]) -> Address:
        """Extrait une adresse FR Core."""
        # Lignes d'adresse
        lines = [line for line in address_data.get("line", []) if line is not None]

        # Code INSEE depuis extension
        insee_code = None
        extensions = address_data.get("extension", [])
        for ext in extensions:
            if "insee-code" in ext.get("url", ""):
                coding = ext.get("valueCoding", {})
                insee_code = coding.get("code")

        # Extensions dans _line pour street details
        street_name_type = None
        street_name_base = None
        lieu_dit = None

        line_extensions = address_data.get("_line", [])
        for line_ext in line_extensions:
            if line_ext:
                line_exts = line_ext.get("extension", [])
                for ext in line_exts:
                    url = ext.get("url", "")
                    if "streetNameType" in url:
                        street_name_type = ext.get("valueString")
                    elif "streetNameBase" in url:
                        street_name_base = ext.get("valueString")
                    elif "lieu-dit" in url:
                        lieu_dit = ext.get("valueString")

        return Address(
            lines=lines,
            city=address_data.get("city"),
            postal_code=address_data.get("postalCode"),
            district=address_data.get("district"),
            country=address_data.get("country"),
            insee_code=insee_code,
            street_name_type=street_name_type,
            street_name_base=street_name_base,
            lieu_dit=lieu_dit,
            use=address_data.get("use"),
            type=address_data.get("type"),
        )

    def extract_contact_info(self, telecoms_data: list[dict[str, Any]]) -> ContactInfo:
        """Extrait les informations de contact FR Core."""
        phones = []
        emails = []
        mssante = []

        for telecom in telecoms_data:
            system = telecom.get("system")
            value = telecom.get("value")

            if not value:
                continue

            # Verifier si MSSante
            is_mssante = False
            mss_metadata = {}

            extensions = telecom.get("extension", [])
            for ext in extensions:
                url = ext.get("url", "")
                if "email-type" in url:
                    coding = ext.get("valueCoding", {})
                    if coding.get("code") == "MSSANTE":
                        is_mssante = True
                elif "mailbox-mss-metadata" in url:
                    mss_metadata = self._extract_mss_metadata(ext)

            if system == "email":
                if is_mssante:
                    mssante.append(
                        MSSanteMailbox(
                            email=value,
                            type=mss_metadata.get("type"),
                            description=mss_metadata.get("description"),
                            responsible=mss_metadata.get("responsible"),
                            service=mss_metadata.get("service"),
                            phone=mss_metadata.get("phone"),
                            digitization=mss_metadata.get("digitization", False),
                            liste_rouge=mss_metadata.get("liste_rouge", False),
                        )
                    )
                else:
                    emails.append(value)
            elif system == "phone":
                phones.append(value)

        return ContactInfo(phones=phones, emails=emails, mssante=mssante)

    def _extract_mss_metadata(self, extension_data: dict[str, Any]) -> dict[str, Any]:
        """Extrait les metadonnees MSSante."""
        result = {}
        sub_extensions = extension_data.get("extension", [])

        for sub_ext in sub_extensions:
            url = sub_ext.get("url", "")
            if url == "type":
                concept = sub_ext.get("valueCodeableConcept", {})
                codings = concept.get("coding", [])
                if codings:
                    result["type"] = codings[0].get("code")
            elif url == "description":
                result["description"] = sub_ext.get("valueString")
            elif url == "responsible":
                result["responsible"] = sub_ext.get("valueString")
            elif url == "service":
                result["service"] = sub_ext.get("valueString")
            elif url == "phone":
                result["phone"] = sub_ext.get("valueString")
            elif url == "digitization":
                result["digitization"] = sub_ext.get("valueBoolean", False)
            elif url == "listeRouge":
                result["liste_rouge"] = sub_ext.get("valueBoolean", False)

        return result

    def extract_smartcards(self, extensions_data: list[dict[str, Any]]) -> list[Smartcard]:
        """Extrait les cartes professionnelles."""
        smartcards = []

        for ext in extensions_data:
            if "smartcard" not in ext.get("url", ""):
                continue

            card_type = None
            number = None
            period = None
            opposition_date = None

            sub_extensions = ext.get("extension", [])
            for sub_ext in sub_extensions:
                url = sub_ext.get("url", "")
                if url == "type":
                    concept = sub_ext.get("valueCodeableConcept", {})
                    codings = concept.get("coding", [])
                    if codings:
                        card_type = codings[0].get("code")
                elif url == "number":
                    number = sub_ext.get("valueString")
                elif url == "period":
                    period = self.extract_period(sub_ext.get("valuePeriod"))
                elif url == "oppositionDate":
                    opposition_date = sub_ext.get("valueDate")

            # Determiner si la carte est valide
            is_valid = False
            if period and not opposition_date:
                today = date.today()
                if period.start:
                    start_date = date.fromisoformat(period.start.split("T")[0])
                    if period.end:
                        end_date = date.fromisoformat(period.end.split("T")[0])
                        is_valid = start_date <= today <= end_date
                    else:
                        is_valid = start_date <= today

            smartcards.append(
                Smartcard(
                    type=card_type,
                    number=number,
                    period=period,
                    opposition_date=opposition_date,
                    is_valid=is_valid,
                )
            )

        return smartcards

    def extract_authorization(
        self, extensions_data: list[dict[str, Any]]
    ) -> Optional[Authorization]:
        """Extrait l'autorisation."""
        for ext in extensions_data:
            if "authorization" not in ext.get("url", "").lower():
                continue

            date_auth = None
            period = None
            date_update = None
            deleted = False

            sub_extensions = ext.get("extension", [])
            for sub_ext in sub_extensions:
                url = sub_ext.get("url", "")
                if url == "dateAuthorization":
                    date_auth = sub_ext.get("valueDate")
                elif url == "periodAuthorization":
                    period = self.extract_period(sub_ext.get("valuePeriod"))
                elif url == "dateUpdateAuthorization":
                    date_update = sub_ext.get("valueDate")
                elif url == "deletedAuthorization":
                    deleted = sub_ext.get("valueBoolean", False)

            # Determiner si l'autorisation est active
            is_active = not deleted
            if is_active and period:
                today = date.today()
                if period.start:
                    start_date = date.fromisoformat(period.start.split("T")[0])
                    if today < start_date:
                        is_active = False
                if period.end:
                    end_date = date.fromisoformat(period.end.split("T")[0])
                    if today > end_date:
                        is_active = False

            return Authorization(
                date=date_auth,
                period=period,
                date_update=date_update,
                deleted=deleted,
                is_active=is_active,
            )

        return None
