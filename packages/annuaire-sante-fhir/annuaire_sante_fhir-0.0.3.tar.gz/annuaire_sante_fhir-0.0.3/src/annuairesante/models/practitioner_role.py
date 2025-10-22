"""Modele PractitionerRole - Situation d'exercice d'un professionnel.

Base sur:
- FR Core PractitionerRole Profile v2.1.0
- AS DP PractitionerRole Profile v1.1.0
"""

from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .common import Coding, ContactInfo, Identifier, Metadata, Period


class PractitionerRole(BaseModel):
    """
    Situation d'exercice d'un professionnel dans une structure.

    Conforme a AS DP PractitionerRole Profile v1.1.0.
    Tous les codes MOS sont resolus en libelles lisibles.

    Note: Dans AS DP, specialty, location et healthcareService ne sont PAS autorises.
    """

    model_config = ConfigDict(populate_by_name=True)

    # References obligatoires
    practitioner_id: str = Field(..., description="ID du professionnel (reference Practitioner)")
    organization_id: str = Field(..., description="ID de l'organisation (reference Organization)")

    # Identifiants de la situation d'exercice
    identifiers: list[Identifier] = Field(
        default_factory=list, description="Identifiants de situation d'exercice"
    )

    # Codes de role/activite - Structure amelioree pour accessibilite
    codes_by_name: dict[str, Union[Coding, list[Coding]]] = Field(
        default_factory=dict,
        description="Codes indexes par nom de systeme MOS. "
        "Ex: codes_by_name['GenreActivite'] -> Coding ou list[Coding]",
    )

    # Codes originaux (garde pour compatibilite)
    codes_raw: list[Coding] = Field(
        default_factory=list,
        description="Codes au format original (liste de Coding)",
        alias="_codes_raw",
    )

    # Periode de la situation d'exercice
    period: Optional[Period] = Field(None, description="Periode de validite de la situation")

    # Contacts (seuls les contacts MSSante sont autorises dans AS DP)
    contacts: ContactInfo = Field(
        default_factory=ContactInfo,
        description="Informations de contact (principalement MSSante)",
    )

    # Metadonnees FHIR
    metadata: Metadata = Field(..., description="Metadonnees FHIR (id, version, profiles, etc.)")

    # Statut actif (obligatoire)
    active: bool = Field(True, description="Statut d'activite de la situation d'exercice")

    # Données FHIR brutes (optionnel)
    fhir_raw: Optional[dict[str, Any]] = Field(
        None, description="Données FHIR brutes complètes (si demandé)"
    )

    def __repr__(self) -> str:
        """Representation textuelle."""
        return (
            f"<PractitionerRole {self.metadata.id} "
            f"(Practitioner: {self.practitioner_id}, Org: {self.organization_id})>"
        )
