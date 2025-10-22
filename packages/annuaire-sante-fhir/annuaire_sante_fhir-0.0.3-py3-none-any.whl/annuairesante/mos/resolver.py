"""Resolveur de codes MOS (Modele des Objets de Sante)."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional, cast

logger = logging.getLogger(__name__)


class MOSResolver:
    """
    Resolveur de codes MOS pour obtenir les libelles.

    Les codes MOS sont references sur https://mos.esante.gouv.fr/NOS/

    Utilise exclusivement les donnees telechargees via MOSDownloader.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Args:
            cache_dir: Repertoire de cache (defaut: $ANNUAIRE_SANTE_CACHE_DIR ou ~/.annuairesante_cache/)
        """
        if cache_dir is None:
            # Verifier la variable d'environnement
            env_cache = os.getenv("ANNUAIRE_SANTE_CACHE_DIR")
            cache_dir = env_cache or os.path.join(Path.home(), ".annuairesante_cache")

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, str] = {}

        # Index telecharge depuis MOS
        self._mos_index: Optional[dict[str, object]] = None
        self._auto_init_attempted = False  # Flag pour eviter les boucles infinies
        self._load_mos_index()

        # Charger le cache existant
        self._load_cache()

    def _load_mos_index(self) -> None:
        """Charge l'index MOS telecharge."""
        mos_dir = self.cache_dir / "mos"
        index_file = mos_dir / "lookup_index.json"

        if index_file.exists():
            try:
                with open(index_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Support ancien format (dict simple) et nouveau format (avec codes/names/mapping)
                if isinstance(data, dict) and "codes" in data:
                    # Nouveau format
                    self._mos_index = data
                    logger.info(
                        "Index MOS charge: %d tables (codes), %d noms lisibles",
                        len(data.get("codes", {})),
                        len(data.get("names", {})),
                    )
                else:
                    # Ancien format - convertir pour compatibilite
                    self._mos_index = {"codes": data, "names": {}, "mapping": {}}
                    logger.info("Index MOS charge (ancien format): %d tables", len(data))
            except Exception as e:
                logger.warning("Erreur chargement index MOS: %s", e)
                self._mos_index = None
        else:
            # Verifier si auto-init est active et n'a pas deja ete tente
            auto_init_value = os.getenv("ANNUAIRE_SANTE_AUTO_INIT_MOS", "false")

            if auto_init_value.lower() in ("true", "1", "yes") and not self._auto_init_attempted:
                self._auto_init_attempted = True  # Marquer comme tente avant d'appeler
                logger.info("Initialisation automatique du cache MOS activee...")
                self._auto_init_cache()
            elif not self._auto_init_attempted:
                logger.warning("Index MOS non trouve: %s", index_file)
                logger.info(
                    "Telechargez les referentiels avec: python examples/download_mos.py essential"
                )
                logger.info(
                    "Ou activez l'initialisation automatique avec ANNUAIRE_SANTE_AUTO_INIT_MOS=true"
                )
                self._mos_index = None
            else:
                # Auto-init deja tente mais a echoue
                logger.warning("Index MOS non disponible apres initialisation automatique")
                self._mos_index = None

    def _auto_init_cache(self) -> None:
        """Initialise automatiquement le cache MOS avec les referentiels essentiels."""
        try:
            # Import ici pour eviter les imports circulaires
            from .downloader import MOSDownloader  # type: ignore[import-untyped]

            logger.info("Telechargement des referentiels MOS essentiels...")

            downloader = MOSDownloader(cache_dir=str(self.cache_dir / "mos"))

            # Telecharger tous les TRE essentiels (R, G, A)
            stats = downloader.download_all(
                force=False,
                include_patterns=[
                    "TRE_R*",
                    "TRE_G*",
                    "TRE_A*",
                ],  # Tous les TRE (tables de reference)
            )

            logger.info(
                "Telechargement termine: %d referentiels telecharges", stats.get("downloaded", 0)
            )

            # Construire l'index de recherche si des fichiers ont ete telecharges
            if stats.get("downloaded", 0) > 0 or stats.get("skipped", 0) > 0:
                logger.info("Construction de l'index de recherche...")
                downloader.build_lookup_index()

            # Recharger l'index (eviter la recursion en chargeant directement)
            mos_dir = self.cache_dir / "mos"
            index_file = mos_dir / "lookup_index.json"
            if index_file.exists():
                with open(index_file, encoding="utf-8") as f:
                    self._mos_index = json.load(f)
                logger.info("Index MOS recharge: %d tables", len(self._mos_index))
            else:
                logger.warning("Index MOS non trouve apres telechargement")
                self._mos_index = None

        except Exception as e:
            logger.error("Erreur lors de l'initialisation automatique du cache MOS: %s", e)
            self._mos_index = None

    def _load_cache(self) -> None:
        """Charge le cache depuis le disque."""
        cache_file = self.cache_dir / "mos_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception:
                pass

    def _save_cache(self) -> None:
        """Sauvegarde le cache sur le disque."""
        cache_file = self.cache_dir / "mos_cache.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def resolve(self, system: str, code: str) -> Optional[str]:
        """
        Resout un code MOS pour obtenir son libelle.

        Args:
            system: URL du systeme (ex: "https://mos.esante.gouv.fr/NOS/TRE_R48-DiplomeEtatFrancais/...")
            code: Code a resoudre (ex: "DE28")

        Returns:
            Libelle du code ou None si non trouve

        Example:
            >>> resolver = MOSResolver()
            >>> resolver.resolve(
            ...     "https://mos.esante.gouv.fr/NOS/TRE_R48-DiplomeEtatFrancais/FHIR/TRE-R48-DiplomeEtatFrancais",
            ...     "DE28"
            ... )
            "Diplome d'État de docteur en medecine"
        """
        # Verifier le cache
        cache_key = f"{system}#{code}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Extraire le nom de la table de reference du systeme
        table = self._extract_table_name(system)
        if not table:
            return None

        # Utiliser l'index MOS telecharge
        if self._mos_index:
            # Essayer avec l'index "codes" (nouveau format ou ancien format converti)
            codes_index_raw = self._mos_index.get("codes", self._mos_index)
            if isinstance(codes_index_raw, dict):
                codes_index = cast(dict[str, Any], codes_index_raw)
                if table in codes_index:
                    table_data_raw = codes_index[table]
                    if isinstance(table_data_raw, dict):
                        table_data = cast(dict[str, str], table_data_raw)
                        display = table_data.get(code)
                        if display:
                            self._cache[cache_key] = display
                            self._save_cache()
                            return display

        # Aucune resolution possible
        return None

    def _extract_table_name(self, system: str) -> Optional[str]:
        """Extrait le nom de table de reference depuis l'URL du systeme."""
        if "/TRE" in system:
            # Ex: ".../TRE_R48-DiplomeEtatFrancais/..." -> "TRE-R48"
            # Ex: ".../TRE-R48-DiplomeEtatFrancais/..." -> "TRE-R48"
            parts = system.split("/TRE")
            if len(parts) > 1:
                # Prendre tout jusqu'au prochain /
                table_part = "TRE" + parts[1].split("/")[0]

                # Extraire juste TRE_RXX ou TRE-RXX
                # Format possible: TRE_R48-DiplomeEtatFrancais ou TRE-R48-DiplomeEtatFrancais

                # Separer par - pour enlever le nom de la table
                if "-" in table_part:
                    # "TRE_R48-DiplomeEtat..." -> ["TRE_R48", "DiplomeEtat..."]
                    code_part = table_part.split("-")[0]
                    # Normaliser avec tirets : TRE_R48 ou TRE-R48 -> TRE-R48
                    return code_part.replace("_", "-")
                else:
                    # Cas ou il n'y a pas de - (rare)
                    return table_part.replace("_", "-")

        # Support pour JDV et ASS
        if "/JDV" in system:
            parts = system.split("/JDV")
            if len(parts) > 1:
                table_part = "JDV" + parts[1].split("/")[0]
                if "-" in table_part:
                    code_part = table_part.split("-")[0]
                    return code_part.replace("_", "-")
                return table_part.replace("_", "-")

        if "/ASS" in system:
            parts = system.split("/ASS")
            if len(parts) > 1:
                table_part = "ASS" + parts[1].split("/")[0]
                if "-" in table_part:
                    code_part = table_part.split("-")[0]
                    return code_part.replace("_", "-")
                return table_part.replace("_", "-")

        return None

    def get_system_name(self, system: str) -> Optional[str]:
        """
        Retourne le nom lisible d'un systeme MOS.

        Args:
            system: URL du systeme (ex: "https://mos.esante.gouv.fr/NOS/TRE_R48-...")

        Returns:
            Nom lisible (ex: "DiplomeEtatFrancais") ou None si non trouve

        Example:
            >>> resolver = MOSResolver()
            >>> resolver.get_system_name(
            ...     "https://mos.esante.gouv.fr/NOS/TRE_R48-DiplomeEtatFrancais/..."
            ... )
            "DiplomeEtatFrancais"
        """
        # Extraire le code de table (TRE-R48)
        table_code = self._extract_table_name(system)
        if not table_code:
            return None

        # Utiliser le mapping pour obtenir le nom lisible
        if self._mos_index and "mapping" in self._mos_index:
            mapping_raw = self._mos_index["mapping"]
            if isinstance(mapping_raw, dict):
                mapping = cast(dict[str, str], mapping_raw)
                return mapping.get(table_code)

        return None

    def reload_index(self) -> None:
        """Recharge l'index MOS depuis le disque."""
        self._load_mos_index()
        logger.info("Index MOS recharge")

    def resolve_coding(self, coding: dict[str, str]) -> str:
        """
        Resout un objet coding FHIR.

        Args:
            coding: Dictionnaire contenant system, code, display

        Returns:
            Libelle (display si present, sinon resolu, sinon code)
        """
        # Si display est deja present, le retourner
        display = coding.get("display")
        if display:
            return str(display)

        # Sinon, essayer de resoudre
        system = coding.get("system")
        code = coding.get("code")

        if system and code:
            resolved = self.resolve(system, code)
            if resolved:
                return resolved

        # Fallback sur le code
        return code or "Unknown"

    def enrich_qualifications(self, qualifications: list) -> list:
        """
        Enrichit une liste de qualifications avec les libelles MOS.

        Args:
            qualifications: Liste de qualifications (depuis PractitionerHelper)

        Returns:
            Liste enrichie avec les libelles
        """
        result = []
        for qual in qualifications:
            enriched_codes = []

            for code_info in qual.get("codes", []):
                display = self.resolve_coding(code_info)
                enriched_codes.append({**code_info, "resolved_display": display})

            result.append({**qual, "codes": enriched_codes})

        return result

    def get_stats(self) -> dict:
        """Retourne les statistiques de l'index MOS."""
        if not self._mos_index:
            return {
                "loaded": False,
                "tables_count": 0,
                "total_codes": 0,
                "readable_names_count": 0,
                "cache_hits": len(self._cache),
            }

        # Support ancien et nouveau format
        codes_index_raw = self._mos_index.get("codes", self._mos_index)
        codes_index = (
            cast(dict[str, Any], codes_index_raw) if isinstance(codes_index_raw, dict) else {}
        )
        names_index_raw = self._mos_index.get("names", {})
        names_index = (
            cast(dict[str, Any], names_index_raw) if isinstance(names_index_raw, dict) else {}
        )

        total_codes = sum(len(codes) for codes in codes_index.values() if isinstance(codes, dict))

        return {
            "loaded": True,
            "tables_count": len(codes_index),
            "total_codes": total_codes,
            "readable_names_count": len(names_index),
            "cache_hits": len(self._cache),
        }


# Instance globale singleton
_resolver = None


def get_resolver() -> MOSResolver:
    """Retourne l'instance singleton du resolveur MOS."""
    global _resolver
    if _resolver is None:
        _resolver = MOSResolver()
    return _resolver


def resolve_code(system: str, code: str) -> Optional[str]:
    """
    Fonction helper pour resoudre un code MOS.

    Args:
        system: URL du systeme MOS
        code: Code a resoudre

    Returns:
        Libelle ou None
    """
    return get_resolver().resolve(system, code)
