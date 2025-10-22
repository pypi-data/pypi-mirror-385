"""Modeles communs reutilisables pour toutes les ressources FHIR."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Period(BaseModel):
    """Periode avec dates de debut et fin."""

    model_config = ConfigDict(populate_by_name=True)

    start: Optional[str] = Field(None, description="Date de debut (format ISO 8601)")
    end: Optional[str] = Field(None, description="Date de fin (format ISO 8601)")


class Coding(BaseModel):
    """Code avec systeme et libelle resolu."""

    model_config = ConfigDict(populate_by_name=True)

    system: Optional[str] = Field(None, description="Systeme de codification (URL)")
    code: Optional[str] = Field(None, description="Code")
    display: Optional[str] = Field(None, description="Libelle resolu via MOS")


class Identifier(BaseModel):
    """Identifiant generique."""

    model_config = ConfigDict(populate_by_name=True)

    system: Optional[str] = Field(None, description="Systeme d'identification")
    value: Optional[str] = Field(None, description="Valeur de l'identifiant")
    type: Optional[str] = Field(None, description="Type d'identifiant (RPPS, FINESS, etc.)")
    use: Optional[str] = Field(None, description="Usage (official, secondary, etc.)")


class Address(BaseModel):
    """Adresse normalisee selon FR Core Address."""

    model_config = ConfigDict(populate_by_name=True)

    lines: list[str] = Field(default_factory=list, description="Lignes d'adresse")
    city: Optional[str] = Field(None, description="Ville")
    postal_code: Optional[str] = Field(None, description="Code postal")
    district: Optional[str] = Field(None, description="Departement")
    country: Optional[str] = Field(None, description="Pays (code ISO 3166-3)")
    insee_code: Optional[str] = Field(None, description="Code INSEE de la commune")
    street_name_type: Optional[str] = Field(None, description="Type de voie (RUE, AVE, etc.)")
    street_name_base: Optional[str] = Field(None, description="Nom de base de la voie")
    lieu_dit: Optional[str] = Field(None, description="Lieu-dit")
    use: Optional[str] = Field(None, description="Usage de l'adresse (home, work, etc.)")
    type: Optional[str] = Field(None, description="Type d'adresse (postal, physical, both)")


class MSSanteMailbox(BaseModel):
    """Boîte aux lettres MSSante (as-ext-mailbox-mss-metadata)."""

    model_config = ConfigDict(populate_by_name=True)

    email: str = Field(..., description="Adresse email MSSante")
    type: Optional[str] = Field(None, description="Type de BAL (ORG, APP, PER, CAB)")
    description: Optional[str] = Field(None, description="Description fonctionnelle")
    responsible: Optional[str] = Field(None, description="Responsable (non renseigne pour PER)")
    service: Optional[str] = Field(None, description="Nom du service de rattachement")
    phone: Optional[str] = Field(None, description="Telephone specifique")
    digitization: bool = Field(False, description="Acceptation de la dematerialisation")
    liste_rouge: bool = Field(False, description="BAL sur liste rouge (non publiable)")


class ContactInfo(BaseModel):
    """Informations de contact normalisees."""

    model_config = ConfigDict(populate_by_name=True)

    phones: list[str] = Field(default_factory=list, description="Numeros de telephone")
    emails: list[str] = Field(default_factory=list, description="Adresses email classiques")
    mssante: list[MSSanteMailbox] = Field(
        default_factory=list, description="Boîtes aux lettres MSSante"
    )


class DataTrace(BaseModel):
    """Tracabilite des donnees (as-ext-data-trace)."""

    model_config = ConfigDict(populate_by_name=True)

    autorite_enregistrement: Optional[str] = Field(
        None, description="Autorite d'enregistrement (AE)"
    )
    systeme_information: Optional[str] = Field(
        None, description="Systeme d'information source (RPPS, FINESS, MSS, CG)"
    )
    date_maj_ae: Optional[str] = Field(
        None, description="Date de mise a jour a l'autorite d'enregistrement"
    )


class Metadata(BaseModel):
    """Metadonnees FHIR communes."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Identifiant technique FHIR de la ressource")
    version_id: Optional[str] = Field(None, description="Version de la ressource")
    last_updated: Optional[str] = Field(None, description="Date de derniere mise a jour")
    source: Optional[str] = Field(None, description="Source des donnees")
    profiles: list[str] = Field(
        default_factory=list, description="Profils FHIR appliques (URLs canoniques)"
    )
    language: Optional[str] = Field(None, description="Langue de la ressource")
    data_trace: Optional[DataTrace] = Field(None, description="Tracabilite des donnees")

    @field_validator("version_id", mode="before")
    @classmethod
    def convert_version_id_to_str(cls, v: object) -> object:
        """Convertit version_id en string (l'API FHIR peut renvoyer un int)."""
        if v is not None:
            return str(v)
        return v


class Smartcard(BaseModel):
    """Carte professionnelle (as-ext-smartcard)."""

    model_config = ConfigDict(populate_by_name=True)

    type: Optional[str] = Field(None, description="Type de carte (CPS, CPF, etc.)")
    number: Optional[str] = Field(None, description="Numero de la carte")
    period: Optional[Period] = Field(None, description="Periode de validite")
    opposition_date: Optional[str] = Field(None, description="Date d'opposition")
    is_valid: bool = Field(False, description="Carte actuellement valide")


class Authorization(BaseModel):
    """Autorisation pour services de sante et equipements (as-ext-authorization)."""

    model_config = ConfigDict(populate_by_name=True)

    date: Optional[str] = Field(None, description="Date de delivrance de l'autorisation")
    period: Optional[Period] = Field(None, description="Periode de mise en œuvre")
    date_update: Optional[str] = Field(None, description="Date de derniere mise a jour")
    deleted: bool = Field(False, description="Autorisation supprimee")
    is_active: bool = Field(False, description="Autorisation actuellement active")


class Qualification(BaseModel):
    """Qualification d'un professionnel."""

    model_config = ConfigDict(populate_by_name=True)

    type: str = Field(..., description="Type de qualification (diplome, profession, etc.)")
    codes: list[Coding] = Field(
        default_factory=list, description="Codes de qualification avec libelles resolus"
    )
    period: Optional[Period] = Field(None, description="Periode de validite")
    issuer: Optional[str] = Field(None, description="Émetteur de la qualification")


class OrganizationType(BaseModel):
    """Type d'organisation avec categorie."""

    model_config = ConfigDict(populate_by_name=True)

    code: Optional[str] = Field(None, description="Code du type")
    display: Optional[str] = Field(None, description="Libelle resolu")
    category: Optional[str] = Field(
        None,
        description="Categorie (organizationType, secteurActiviteRASS, "
        "categorieEtablissement, statutJuridiqueINSEE, activiteINSEE, "
        "sphParticipation, modeFixationTarifs, modeleFinancementEtablissement)",
    )
