"""Modele HealthcareService - Service/Activite de sante.

Base sur:
- FR Core HealthcareService Profile v2.1.0
- AS DP HealthcareService Healthcare Activity Profile v1.1.0
"""

from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .common import Authorization, Coding, Identifier, Metadata


class HealthcareService(BaseModel):
    """
    Service ou activite de sante reglementee.

    Conforme a AS DP HealthcareService Healthcare Activity Profile v1.1.0.
    Tous les codes MOS sont resolus en libelles lisibles.
    """

    model_config = ConfigDict(populate_by_name=True)

    # Identifiants (ARHGOS obligatoire)
    identifiers: list[Identifier] = Field(
        default_factory=list, description="Identifiants du service (ARHGOS requis)"
    )

    # Nom du service
    name: Optional[str] = Field(None, description="Nom du service de sante")

    # Organisation qui fournit le service
    organization_id: Optional[str] = Field(
        None, description="ID de l'organisation fournissant le service (providedBy)"
    )

    # Autorisation (as-ext-authorization)
    authorization: Optional[Authorization] = Field(
        None, description="Autorisation d'activite de soins ou d'equipement"
    )

    # Categories du service - Structure amelioree pour accessibilite
    categories_by_name: dict[str, Union[Coding, list[Coding]]] = Field(
        default_factory=dict,
        description="Modalites d'activite indexees par nom de systeme MOS",
    )
    categories_raw: list[Coding] = Field(
        default_factory=list, description="Categories au format original", alias="_categories_raw"
    )

    # Types d'activite - Structure amelioree pour accessibilite
    types_by_name: dict[str, Union[Coding, list[Coding]]] = Field(
        default_factory=dict,
        description="Types d'activite indexes par nom de systeme MOS",
    )
    types_raw: list[Coding] = Field(
        default_factory=list, description="Types au format original", alias="_types_raw"
    )

    # Caracteristiques - Structure amelioree pour accessibilite
    characteristics_by_name: dict[str, Union[Coding, list[Coding]]] = Field(
        default_factory=dict,
        description="Formes d'activite indexees par nom de systeme MOS",
    )
    characteristics_raw: list[Coding] = Field(
        default_factory=list,
        description="Caracteristiques au format original",
        alias="_characteristics_raw",
    )

    # Eligibilite/Clientele - Structure amelioree pour accessibilite
    eligibility_by_name: dict[str, Union[Coding, list[Coding]]] = Field(
        default_factory=dict,
        description="Clientele eligible indexee par nom de systeme MOS",
    )
    eligibility_raw: list[Coding] = Field(
        default_factory=list,
        description="Eligibilite au format original",
        alias="_eligibility_raw",
    )

    # Metadonnees FHIR
    metadata: Metadata = Field(..., description="Metadonnees FHIR (id, version, profiles, etc.)")

    # Statut actif (obligatoire)
    active: bool = Field(True, description="Statut d'activite du service")

    # Données FHIR brutes (optionnel)
    fhir_raw: Optional[dict[str, Any]] = Field(
        None, description="Données FHIR brutes complètes (si demandé)"
    )

    def __repr__(self) -> str:
        """Representation textuelle."""
        arhgos = next(
            (i.value for i in self.identifiers if "arhgos" in (i.system or "").lower()), None
        )
        return f"<HealthcareService {self.name or self.metadata.id} (ARHGOS: {arhgos})>"
