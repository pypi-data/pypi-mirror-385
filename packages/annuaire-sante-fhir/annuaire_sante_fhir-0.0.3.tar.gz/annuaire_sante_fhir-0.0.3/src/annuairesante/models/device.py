"""Modele Device - Équipement materiel lourd.

Base sur:
- AS DP Device Profile v1.1.0
"""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import Authorization, Coding, Identifier, Metadata


class Device(BaseModel):
    """
    Équipement materiel lourd de sante.

    Conforme a AS DP Device Profile v1.1.0.
    Tous les codes MOS sont resolus en libelles lisibles.
    """

    model_config = ConfigDict(populate_by_name=True)

    # Identifiants (ARHGOS obligatoire)
    identifiers: list[Identifier] = Field(
        default_factory=list, description="Identifiants de l'equipement (ARHGOS requis)"
    )

    # Statut (obligatoire: active, inactive, etc.)
    status: str = Field(..., description="Statut de disponibilite de l'equipement")

    # Fabricant
    manufacturer: Optional[str] = Field(None, description="Fabricant de l'equipement")

    # Type d'equipement (TRE_R272)
    device_type: Optional[Coding] = Field(
        None,
        description="Type d'equipement materiel lourd avec libelle resolu "
        "(TRE_R272-EquipementMaterielLourd)",
    )

    # Proprietaire
    owner_organization_id: Optional[str] = Field(
        None, description="ID de l'organisation proprietaire (owner)"
    )

    # Autorisation (as-ext-authorization)
    authorization: Optional[Authorization] = Field(
        None, description="Autorisation d'equipement materiel lourd"
    )

    # Metadonnees FHIR
    metadata: Metadata = Field(..., description="Metadonnees FHIR (id, version, profiles, etc.)")

    # Données FHIR brutes (optionnel)
    fhir_raw: Optional[dict[str, Any]] = Field(
        None, description="Données FHIR brutes complètes (si demandé)"
    )

    def __repr__(self) -> str:
        """Representation textuelle."""
        arhgos = next(
            (i.value for i in self.identifiers if "arhgos" in (i.system or "").lower()), None
        )
        return f"<Device {self.manufacturer or self.metadata.id} (ARHGOS: {arhgos})>"
