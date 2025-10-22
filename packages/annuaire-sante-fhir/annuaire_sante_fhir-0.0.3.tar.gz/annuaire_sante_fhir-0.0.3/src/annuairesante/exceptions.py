"""Exceptions personnalisees pour le client Annuaire Sante."""


class AnnuaireSanteError(Exception):
    """Erreur de base pour toutes les erreurs du client."""

    pass


class AuthenticationError(AnnuaireSanteError):
    """Erreur d'authentification (cle API manquante ou invalide)."""

    pass


class NotFoundError(AnnuaireSanteError):
    """Ressource non trouvee (404)."""

    pass


class ValidationError(AnnuaireSanteError):
    """Erreur de validation des parametres (400)."""

    pass


class RateLimitError(AnnuaireSanteError):
    """Limite de taux d'appels API depassee (429)."""

    pass


class ServerError(AnnuaireSanteError):
    """Erreur serveur (5xx)."""

    pass


class TransformationError(AnnuaireSanteError):
    """Erreur lors de la transformation FHIR -> JSON."""

    pass
