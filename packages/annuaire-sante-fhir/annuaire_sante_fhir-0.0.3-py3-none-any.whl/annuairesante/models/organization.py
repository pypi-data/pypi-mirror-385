"""Modele Organization - Structure de sante.

Base sur:
- FR Core Organization Profile v2.1.0
- AS DP Organization Profile v1.1.0
"""

from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .common import Address, ContactInfo, Metadata, OrganizationType, Period


class OrganizationIdentifiers(BaseModel):
    """Identifiants d'une organisation (slices AS DP Organization)."""

    model_config = ConfigDict(populate_by_name=True)

    idnst: Optional[str] = Field(None, description="Identifiant National de Structure")
    finess: Optional[str] = Field(
        None, description="FINESS (priorite FINEJ puis FINEG si les deux presents)"
    )
    finej: Optional[str] = Field(None, description="FINESS Juridique")
    fineg: Optional[str] = Field(None, description="FINESS Geographique")
    siren: Optional[str] = Field(None, description="SIREN (9 chiffres)")
    siret: Optional[str] = Field(None, description="SIRET (14 chiffres)")
    adeli_rang: Optional[str] = Field(None, description="Numero ADELI de rang")
    rpps_rang: Optional[str] = Field(None, description="Numero RPPS de rang")
    internal_id: Optional[str] = Field(None, description="Identifiant interne")


class Organization(BaseModel):
    """
    Structure de sante avec donnees normalisees DB-ready.

    Conforme a AS DP Organization Profile v1.1.0.
    Tous les codes MOS sont resolus en libelles lisibles.
    """

    model_config = ConfigDict(populate_by_name=True)

    # Identifiants
    identifiers: OrganizationIdentifiers = Field(..., description="Identifiants de l'organisation")

    # Informations de base
    name: Optional[str] = Field(None, description="Nom de l'organisation")
    aliases: list[str] = Field(default_factory=list, description="Noms alternatifs")
    short_name: Optional[str] = Field(
        None, description="Nom court (extension fr-core-organization-short-name)"
    )
    description: Optional[str] = Field(
        None, description="Description de l'organisation (extension)"
    )

    # Types d'organisation - Structure amelioree pour accessibilite
    types_by_category: dict[str, Union[OrganizationType, list[OrganizationType]]] = Field(
        default_factory=dict,
        description="Types indexes par categorie (organizationType, secteurActiviteRASS, etc.). "
        "Ex: types_by_category['secteurActiviteRASS'] -> OrganizationType ou list[OrganizationType]",
    )

    # Type principal (sans categorie specifique)
    primary_type: Optional[OrganizationType] = Field(
        None, description="Type principal de l'organisation (category=null dans FHIR)"
    )

    # Types originaux (garde pour compatibilite)
    types_raw: list[OrganizationType] = Field(
        default_factory=list,
        description="Types au format original (liste de OrganizationType)",
        alias="_types_raw",
    )

    # Periode d'activite (organization-period extension)
    period: Optional[Period] = Field(None, description="Periode d'activite de l'organisation")

    # Extensions specifiques
    pharmacy_licence: Optional[str] = Field(
        None, description="Numero de licence de pharmacie (as-ext-organization-pharmacy-licence)"
    )
    pricing_model: Optional[str] = Field(
        None, description="Mode de fixation des tarifs (extension)"
    )
    budget_type: Optional[str] = Field(
        None, description="Type de budget (lettre budgetaire, extension)"
    )
    closing_type: Optional[str] = Field(None, description="Type de fermeture (extension)")
    authorization_deadline: Optional[str] = Field(
        None, description="Date limite d'autorisation (extension)"
    )

    # Adresses (FR Core Address)
    addresses: list[Address] = Field(default_factory=list, description="Adresses de l'organisation")

    # Contacts (FR Core ContactPoint)
    contacts: ContactInfo = Field(
        default_factory=ContactInfo, description="Informations de contact"
    )

    # Organisation parente
    parent_organization_id: Optional[str] = Field(
        None, description="ID de l'organisation parente (partOf)"
    )

    # Metadonnees FHIR
    metadata: Metadata = Field(..., description="Metadonnees FHIR (id, version, profiles, etc.)")

    # Statut actif (obligatoire, defaut true)
    active: bool = Field(True, description="Statut d'activite de l'organisation")

    # Données FHIR brutes (optionnel)
    fhir_raw: Optional[dict[str, Any]] = Field(
        None, description="Données FHIR brutes complètes (si demandé)"
    )

    def __repr__(self) -> str:
        """Representation textuelle."""
        finess = self.identifiers.finess or self.identifiers.finej or self.identifiers.fineg
        return f"<Organization {self.name} (FINESS: {finess})>"

    # Helper methods pour acceder facilement aux types communs
    def get_secteur_activite(self) -> Optional[OrganizationType]:
        """Retourne le secteur d'activite RASS."""
        sector: Union[OrganizationType, list[OrganizationType], None] = self.types_by_category.get(
            "secteurActiviteRASS"
        )
        if isinstance(sector, list) and sector:
            return sector[0]
        return sector if isinstance(sector, OrganizationType) else None

    def get_statut_juridique(self) -> Optional[OrganizationType]:
        """Retourne le statut juridique INSEE."""
        statut: Union[OrganizationType, list[OrganizationType], None] = self.types_by_category.get(
            "statutJuridiqueINSEE"
        )
        if isinstance(statut, list) and statut:
            return statut[0]
        return statut if isinstance(statut, OrganizationType) else None

    def get_categorie_etablissement(self) -> Optional[OrganizationType]:
        """Retourne la categorie d'etablissement."""
        cat: Union[OrganizationType, list[OrganizationType], None] = self.types_by_category.get(
            "categorieEtablissement"
        )
        if isinstance(cat, list) and cat:
            return cat[0]
        return cat if isinstance(cat, OrganizationType) else None
