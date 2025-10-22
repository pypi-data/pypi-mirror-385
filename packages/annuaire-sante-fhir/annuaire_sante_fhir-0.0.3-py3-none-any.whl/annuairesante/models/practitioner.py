"""Modele Practitioner - Professionnel de sante.

Base sur:
- FR Core Practitioner Profile v2.1.0
- AS DP Practitioner Profile v1.1.0
"""

from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .common import (
    Address,
    Coding,
    ContactInfo,
    Metadata,
    Qualification,
    Smartcard,
)


class PractitionerIdentifiers(BaseModel):
    """Identifiants d'un professionnel (slices AS DP Practitioner)."""

    model_config = ConfigDict(populate_by_name=True)

    idnps: str = Field(
        ..., description="Identifiant National des Professionnels de Sante (obligatoire)"
    )
    rpps: str = Field(..., description="Numero RPPS - 11 chiffres (obligatoire)")
    adeli: Optional[str] = Field(None, description="Numero ADELI")


class PractitionerName(BaseModel):
    """Nom d'un professionnel (FR Core HumanName)."""

    model_config = ConfigDict(populate_by_name=True)

    family: Optional[str] = Field(None, description="Nom de famille")
    given: list[str] = Field(default_factory=list, description="Prenoms")
    prefix: Optional[str] = Field(
        None, description="Civilite (0..1, value set JDV_J78-Civilite-RASS)"
    )
    suffix: list[str] = Field(
        default_factory=list,
        description="Titres d'exercice (0..*, value set JDV_J79-CiviliteExercice-RASS)",
    )
    full_text: Optional[str] = Field(None, description="Nom complet formate")
    assembly_order: Optional[str] = Field(
        None, description="Ordre d'assemblage prefere des elements du nom"
    )


class Communication(BaseModel):
    """Langue de communication."""

    model_config = ConfigDict(populate_by_name=True)

    code: Optional[str] = Field(None, description="Code de langue")
    display: Optional[str] = Field(None, description="Libelle de la langue (resolu via MOS)")


class Practitioner(BaseModel):
    """
    Professionnel de sante avec donnees normalisees DB-ready.

    Conforme a AS DP Practitioner Profile v1.1.0.
    Tous les codes MOS sont resolus en libelles lisibles.
    """

    model_config = ConfigDict(populate_by_name=True)

    # Identifiants (obligatoires: IDNPS + RPPS)
    identifiers: PractitionerIdentifiers = Field(..., description="Identifiants du professionnel")

    # Nom (FR Core HumanName)
    name: Optional[PractitionerName] = Field(None, description="Nom du professionnel")

    # Informations personnelles
    gender: Optional[str] = Field(None, description="Genre (male, female, other, unknown)")
    birth_date: Optional[str] = Field(None, description="Date de naissance (YYYY-MM-DD)")
    deceased: bool = Field(False, description="Professionnel decede")
    deceased_date: Optional[str] = Field(None, description="Date de deces")

    # Contacts (FR Core ContactPoint)
    contacts: ContactInfo = Field(
        default_factory=ContactInfo, description="Informations de contact"
    )

    # Adresses (FR Core Address)
    addresses: list[Address] = Field(default_factory=list, description="Adresses du professionnel")

    # Qualifications - Structure amelioree pour accessibilite
    qualifications: dict[str, dict[str, Union[Coding, list[Coding]]]] = Field(
        default_factory=dict,
        description="Qualifications indexees par type puis par nom de systeme MOS. "
        "Ex: qualifications['profession']['ProfessionSante'] -> Coding ou list[Coding]",
    )

    # Qualifications originales (garde pour compatibilite et reference)
    qualifications_raw: list[Qualification] = Field(
        default_factory=list,
        description="Qualifications au format original (liste de Qualification)",
        alias="_qualifications_raw",
    )

    # Cartes professionnelles (as-ext-smartcard)
    smartcards: list[Smartcard] = Field(
        default_factory=list, description="Cartes professionnelles (CPS, CPF, etc.)"
    )

    # Langues de communication
    communications: list[Communication] = Field(
        default_factory=list, description="Langues parlees par le professionnel"
    )

    # Metadonnees FHIR
    metadata: Metadata = Field(..., description="Metadonnees FHIR (id, version, profiles, etc.)")

    # Statut actif (obligatoire dans AS DP)
    active: bool = Field(True, description="Statut d'activite du professionnel")

    # Données FHIR brutes (optionnel)
    fhir_raw: Optional[dict[str, Any]] = Field(
        None, description="Données FHIR brutes complètes (si demandé)"
    )

    def __repr__(self) -> str:
        """Representation textuelle."""
        name_str = (
            self.name.full_text
            if self.name and self.name.full_text
            else f"{self.name.given[0] if self.name and self.name.given else ''} {self.name.family if self.name else ''}"
        )
        return f"<Practitioner {name_str.strip()} (RPPS: {self.identifiers.rpps})>"

    # Helper methods pour acceder facilement aux qualifications communes
    def get_profession(self) -> Optional[Coding]:
        """Retourne la profession principale (TRE_G15-ProfessionSante ou TRE-G15)."""
        profession_dict = self.qualifications.get("profession", {})
        # Essayer avec le nom lisible, puis le code de table comme fallback
        prof: Union[Coding, list[Coding], None] = profession_dict.get(
            "ProfessionSante"
        ) or profession_dict.get("TRE-G15")
        # Si c'est une liste, prendre le premier element
        if isinstance(prof, list) and prof:
            return prof[0]
        return prof if isinstance(prof, Coding) else None

    def get_diploma(self) -> Optional[Coding]:
        """Retourne le diplome principal (TRE_R48-DiplomeEtatFrancais ou TRE-R48)."""
        diplome_dict = self.qualifications.get("diplome", {})
        # Essayer avec le nom lisible, puis le code de table comme fallback
        diplome: Union[Coding, list[Coding], None] = diplome_dict.get(
            "DiplomeEtatFrancais"
        ) or diplome_dict.get("TRE-R48")
        # Si c'est une liste, prendre le premier element
        if isinstance(diplome, list) and diplome:
            return diplome[0]
        return diplome if isinstance(diplome, Coding) else None

    def get_category(self) -> Optional[Coding]:
        """Retourne la categorie professionnelle (TRE_R09-CategorieProfessionnelle ou TRE-R09)."""
        profession_dict = self.qualifications.get("profession", {})
        # Essayer avec le nom lisible, puis le code de table comme fallback
        cat: Union[Coding, list[Coding], None] = profession_dict.get(
            "CategorieProfessionnelle"
        ) or profession_dict.get("TRE-R09")
        # Si c'est une liste, prendre le premier element
        if isinstance(cat, list) and cat:
            return cat[0]
        return cat if isinstance(cat, Coding) else None
