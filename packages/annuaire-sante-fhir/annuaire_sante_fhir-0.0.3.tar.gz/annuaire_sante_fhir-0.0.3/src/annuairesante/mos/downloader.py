"""Telechargeur et gestionnaire de referentiels MOS/NOS depuis esante.gouv.fr."""

import json
import os
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Optional, cast
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup


class MOSDownloader:
    """
    Telechargeur de referentiels MOS/NOS depuis https://mos.esante.gouv.fr/NOS/

    Gere le telechargement incremental base sur les dates de modification.
    """

    BASE_URL = "https://mos.esante.gouv.fr/NOS/"

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Args:
            cache_dir: Repertoire de cache (defaut: $ANNUAIRE_SANTE_CACHE_DIR/mos ou ~/.annuairesante_cache/mos/)
        """
        cache_path: Path
        if cache_dir is None:
            # Verifier la variable d'environnement
            env_cache = os.getenv("ANNUAIRE_SANTE_CACHE_DIR")
            if env_cache:
                cache_path = Path(env_cache) / "mos"
            else:
                cache_path = Path.home() / ".annuairesante_cache" / "mos"
        else:
            cache_path = Path(cache_dir)

        self.cache_dir = cache_path
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Fichier de metadonnees pour tracker les dates de mise a jour
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()

        # Statistiques de telechargement
        self.stats = {"downloaded": 0, "skipped": 0, "errors": 0, "total": 0}

    def _load_metadata(self) -> dict[str, object]:
        """Charge les metadonnees de telechargement."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, encoding="utf-8") as f:
                    data: dict[str, object] = json.load(f)
                    return data
            except Exception:
                pass
        return {"last_full_sync": None, "terminologies": {}}

    def _save_metadata(self) -> None:
        """Sauvegarde les metadonnees."""
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Erreur sauvegarde metadonnees: {e}")

    def list_terminologies(self, force_refresh: bool = False) -> list[dict[str, Optional[str]]]:
        """
        Liste tous les referentiels disponibles (TRE_*, JDV_*, ASS_*).

        Args:
            force_refresh: Force le rafraîchissement de la liste

        Returns:
            Liste de dicts avec 'name', 'url', 'last_modified'
        """
        print("📋 Recuperation de la liste des referentiels...")

        try:
            response = httpx.get(self.BASE_URL, timeout=30.0, follow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            terminologies = []

            for link in soup.find_all("a"):
                href_raw = link.get("href", "")
                # Convert BeautifulSoup's AttributeValueList/None to str
                href = str(href_raw) if href_raw else ""

                # Filtrer les referentiels TRE, JDV et ASS
                if any(href.startswith(prefix) for prefix in ["TRE_", "JDV_", "ASS_"]):
                    name = href.rstrip("/")
                    url = urljoin(self.BASE_URL, href)

                    # Extraire la date de modification si disponible
                    parent = link.parent
                    last_modified = None
                    if parent:
                        next_sibling = parent.find_next_sibling()
                        if next_sibling:
                            date_text = next_sibling.get_text(strip=True)
                            last_modified = self._parse_date(date_text)

                    terminologies.append({"name": name, "url": url, "last_modified": last_modified})

            print(f"✅ {len(terminologies)} referentiels trouves")
            return terminologies

        except Exception as e:
            print(f"❌ Erreur lors de la recuperation de la liste: {e}")
            return []

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse une date du format Apache directory listing."""
        try:
            # Format: "2024-01-15 10:30"
            dt = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M")
            return dt.isoformat()
        except Exception:
            return None

    def download_terminology(self, name: str, force: bool = False) -> bool:
        """
        Telecharge un referentiel specifique.

        Args:
            name: Nom du referentiel (ex: "TRE_R48-DiplomeEtatFrancais")
            force: Force le telechargement meme si deja a jour

        Returns:
            True si telecharge, False si skippe ou erreur
        """
        # Construire l'URL du fichier JSON FHIR
        # Pattern: /NOS/{name}/FHIR/{normalized-name}/{name}-FHIR.json
        # Ex: TRE_R48-DiplomeEtatFrancais -> TRE-R48-DiplomeEtatFrancais
        normalized_name = name.replace("_", "-")

        base_url = urljoin(self.BASE_URL, f"{name}/FHIR/{normalized_name}/")
        json_url = urljoin(base_url, f"{name}-FHIR.json")

        # Verifier si mise a jour necessaire
        terminologies = cast(dict[str, Any], self.metadata.get("terminologies", {}))
        if not force and name in terminologies:
            # Recuperer la date de derniere modification sur le serveur
            try:
                head_response = httpx.head(json_url, timeout=10.0, follow_redirects=True)
                server_last_modified = head_response.headers.get("Last-Modified")

                if server_last_modified:
                    # Parser la date du serveur (format HTTP-date)
                    server_date = parsedate_to_datetime(server_last_modified)

                    # Comparer avec la date de telechargement local
                    term_meta = cast(dict[str, Any], terminologies.get(name, {}))
                    local_date_str = term_meta.get("downloaded_at")
                    if local_date_str:
                        local_date = datetime.fromisoformat(local_date_str)

                        # Si le serveur n'a pas de version plus recente, skip
                        if server_date.replace(tzinfo=None) <= local_date:
                            print(
                                f"⏭️  {name}: a jour (serveur: {server_date.strftime('%Y-%m-%d %H:%M')})"
                            )
                            self.stats["skipped"] += 1
                            return False
                        else:
                            print(
                                f"🔄 {name}: mise a jour disponible (serveur: {server_date.strftime('%Y-%m-%d %H:%M')})"
                            )
                    else:
                        print(f"⏭️  {name}: deja en cache")
                        self.stats["skipped"] += 1
                        return False
                else:
                    # Pas de Last-Modified header, verifier juste l'existence
                    print(f"⏭️  {name}: deja en cache (pas de date serveur)")
                    self.stats["skipped"] += 1
                    return False

            except Exception as e:
                # En cas d'erreur HEAD, continuer avec le telechargement
                print(f"⚠️  {name}: impossible de verifier la date ({e}), telechargement...")

        try:
            # Telecharger le fichier JSON FHIR
            print(f"⬇️  Telechargement de {name}...")
            response = httpx.get(json_url, timeout=30.0, follow_redirects=True)
            response.raise_for_status()

            # Sauvegarder le fichier
            output_file = self.cache_dir / f"{name}-FHIR.json"
            output_file.write_bytes(response.content)

            # Recuperer la date de modification du serveur
            server_last_modified = response.headers.get("Last-Modified")
            server_date_iso = None
            if server_last_modified:
                try:
                    server_date = parsedate_to_datetime(server_last_modified)
                    server_date_iso = server_date.isoformat()
                except Exception:
                    pass

            # Mettre a jour les metadonnees
            terminologies = cast(dict[str, Any], self.metadata.get("terminologies", {}))
            terminologies[name] = {
                "downloaded_at": datetime.now().isoformat(),
                "server_last_modified": server_date_iso,
                "file": str(output_file),
                "size": len(response.content),
            }
            self.metadata["terminologies"] = terminologies
            self._save_metadata()

            print(f"✅ {name}: telecharge ({len(response.content)} octets)")
            self.stats["downloaded"] += 1
            return True

        except Exception as e:
            print(f"❌ {name}: erreur - {e}")
            self.stats["errors"] += 1
            return False

    def parse_tabs_file(self, terminology_name: str) -> list[dict[str, str]]:
        """
        Parse un fichier JSON FHIR et retourne les entrees.

        Args:
            terminology_name: Nom du referentiel

        Returns:
            Liste de dicts avec 'code', 'display', etc.
        """
        json_file = self.cache_dir / f"{terminology_name}-FHIR.json"

        if not json_file.exists():
            raise FileNotFoundError(f"Fichier non trouve: {json_file}")

        entries = []

        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            resource_type = data.get("resourceType")

            # CodeSystem (TRE) : concept[] directement a la racine
            if resource_type == "CodeSystem":
                concepts = data.get("concept", [])
                for concept in concepts:
                    entry = {
                        "code": concept.get("code"),
                        "display": concept.get("display"),
                        "definition": concept.get("definition"),
                        "property": concept.get("property", []),
                    }
                    entries.append(entry)

            # ValueSet (JDV, ASS) : compose.include[].concept[]
            elif resource_type == "ValueSet":
                compose = data.get("compose", {})
                includes = compose.get("include", [])

                for include in includes:
                    concepts = include.get("concept", [])
                    for concept in concepts:
                        entry = {
                            "code": concept.get("code"),
                            "display": concept.get("display"),
                            "designation": concept.get("designation", []),
                        }
                        entries.append(entry)

            return entries

        except Exception as e:
            print(f"❌ Erreur parsing {terminology_name}: {e}")
            return []

    def parse_fhir_json(self, terminology_name: str) -> list[dict[str, str]]:
        """
        Alias pour parse_tabs_file (pour compatibilite).
        Parse un fichier JSON FHIR.
        """
        return self.parse_tabs_file(terminology_name)

    def download_all(
        self,
        force: bool = False,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
    ) -> dict[str, int]:
        """
        Telecharge tous les referentiels.

        Args:
            force: Force le telechargement meme si deja a jour
            include_patterns: Liste de patterns a inclure (ex: ["TRE_R*", "JDV_J1*"])
            exclude_patterns: Liste de patterns a exclure

        Returns:
            Statistiques de telechargement
        """
        print("=" * 70)
        print("🚀 TÉLÉCHARGEMENT DES RÉFÉRENTIELS MOS/NOS")
        print("=" * 70)

        # Reinitialiser les stats
        self.stats = {"downloaded": 0, "skipped": 0, "errors": 0, "total": 0}

        # Lister les referentiels
        terminologies = self.list_terminologies()

        # Filtrer selon les patterns
        if include_patterns or exclude_patterns:
            terminologies = self._filter_terminologies(
                terminologies, include_patterns, exclude_patterns
            )

        self.stats["total"] = len(terminologies)

        print(f"\n📦 {len(terminologies)} referentiels a traiter\n")

        # Telecharger chaque referentiel
        for i, term in enumerate(terminologies, 1):
            print(f"[{i}/{len(terminologies)}] ", end="")
            term_name = term.get("name")
            if term_name:
                self.download_terminology(term_name, force=force)

        # Mettre a jour la date de synchronisation complete
        self.metadata["last_full_sync"] = datetime.now().isoformat()
        self._save_metadata()

        # Afficher le resume
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ")
        print("=" * 70)
        print(f"Total:        {self.stats['total']}")
        print(f"Telecharges:  {self.stats['downloaded']}")
        print(f"Skippes:      {self.stats['skipped']}")
        print(f"Erreurs:      {self.stats['errors']}")
        print("=" * 70)

        return self.stats

    def _filter_terminologies(
        self,
        terminologies: list[dict],
        include_patterns: Optional[list[str]],
        exclude_patterns: Optional[list[str]],
    ) -> list[dict]:
        """Filtre les referentiels selon les patterns."""
        filtered = terminologies

        if include_patterns:
            filtered = [
                t
                for t in filtered
                if any(self._match_pattern(t["name"], p) for p in include_patterns)
            ]

        if exclude_patterns:
            filtered = [
                t
                for t in filtered
                if not any(self._match_pattern(t["name"], p) for p in exclude_patterns)
            ]

        return filtered

    def _match_pattern(self, name: str, pattern: str) -> bool:
        """Verifie si un nom correspond a un pattern (avec wildcards)."""
        # Convertir le pattern en regex
        regex_pattern = pattern.replace("*", ".*").replace("?", ".")
        return bool(re.match(f"^{regex_pattern}$", name))

    def build_lookup_index(self) -> dict[str, Any]:
        """
        Construit un index de recherche rapide pour tous les referentiels telecharges.

        Returns:
            Dict avec 3 sections:
            - codes: Dict[table_code, Dict[code, display]] (ex: "TRE-R48")
            - names: Dict[table_name, Dict[code, display]] (ex: "DiplomeEtatFrancais")
            - mapping: Dict[table_code, table_name] (ex: "TRE-R48" -> "DiplomeEtatFrancais")
        """
        print("🔨 Construction de l'index de recherche...")

        index_codes: dict[str, dict[str, str]] = {}
        index_names: dict[str, dict[str, str]] = {}
        mapping: dict[str, str] = {}

        terminologies = cast(dict[str, Any], self.metadata.get("terminologies", {}))
        for term_name in terminologies:
            try:
                entries = self.parse_fhir_json(term_name)

                # Extraire le nom de table normalise (TRE-R48)
                table_code = self._extract_table_name(term_name)

                # Extraire le nom lisible (DiplomeEtatFrancais)
                table_name = self._extract_readable_name(term_name)

                if table_code and table_name:
                    index_codes[table_code] = {}
                    index_names[table_name] = {}
                    mapping[table_code] = table_name

                    for entry in entries:
                        code = entry.get("code")
                        display = entry.get("display")

                        if code and display:
                            index_codes[table_code][code] = display
                            index_names[table_name][code] = display

                    print(f"  ✅ {table_code} ({table_name}): {len(index_codes[table_code])} codes")

            except Exception as e:
                print(f"  ⚠️  {term_name}: {e}")

        # Construire l'index complet
        full_index = {"codes": index_codes, "names": index_names, "mapping": mapping}

        # Sauvegarder l'index
        index_file = self.cache_dir / "lookup_index.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(full_index, f, indent=2, ensure_ascii=False)

        print(f"✅ Index sauvegarde: {index_file}")
        print(f"📊 {len(index_codes)} tables indexees")
        print(f"📋 Index codes: {len(index_codes)} tables")
        print(f"📋 Index noms: {len(index_names)} noms lisibles")

        return full_index

    def _extract_table_name(self, terminology_name: str) -> Optional[str]:
        """Extrait le nom de table normalise (code court)."""
        # TRE_R48-DiplomeEtatFrancais -> TRE-R48
        # JDV_J01-XdsAuthorSpecialty-CISIS -> JDV-J01
        # ASS_A11-CorresModeleCDA -> ASS-A11

        match = re.match(r"^(TRE|JDV|ASS)_([A-Z]\d+)", terminology_name)
        if match:
            return f"{match.group(1)}-{match.group(2)}"

        return None

    def _extract_readable_name(self, terminology_name: str) -> Optional[str]:
        """Extrait le nom lisible depuis le nom du referentiel."""
        # TRE_R48-DiplomeEtatFrancais -> DiplomeEtatFrancais
        # JDV_J01-XdsAuthorSpecialty-CISIS -> XdsAuthorSpecialty-CISIS
        # ASS_A11-CorresModeleCDA -> CorresModeleCDA

        # Pattern: (TRE|JDV|ASS)_([A-Z]\d+)-(.+)
        match = re.match(r"^(TRE|JDV|ASS)_[A-Z]\d+-(.+)$", terminology_name)
        if match:
            return match.group(2)  # Partie après le code

        return None

    def get_stats(self) -> dict:
        """Retourne les statistiques de cache."""
        terminologies = cast(dict[str, Any], self.metadata.get("terminologies", {}))

        total_size = sum(
            Path(cast(str, meta.get("file", ""))).stat().st_size
            for meta in terminologies.values()
            if isinstance(meta, dict)
            and meta.get("file")
            and Path(cast(str, meta["file"])).exists()
        )

        return {
            "terminologies_count": len(terminologies),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "last_sync": self.metadata.get("last_full_sync"),
            "cache_dir": str(self.cache_dir),
        }

    def check_updates(
        self,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """
        Verifie les mises a jour disponibles sans telecharger.

        Args:
            include_patterns: Patterns a inclure
            exclude_patterns: Patterns a exclure

        Returns:
            Liste des referentiels avec mises a jour disponibles
        """
        print("🔍 Verification des mises a jour disponibles...\n")

        updates_available = []
        checked = 0

        terminologies = cast(dict[str, Any], self.metadata.get("terminologies", {}))
        for name, meta in terminologies.items():
            # Filtrer selon les patterns
            if include_patterns and not any(self._match_pattern(name, p) for p in include_patterns):
                continue
            if exclude_patterns and any(self._match_pattern(name, p) for p in exclude_patterns):
                continue

            checked += 1

            try:
                # Construire l'URL du fichier JSON FHIR
                normalized_name = name.replace("_", "-")
                base_url = urljoin(self.BASE_URL, f"{name}/FHIR/{normalized_name}/")
                json_url = urljoin(base_url, f"{name}-FHIR.json")

                # HEAD request pour obtenir la date
                head_response = httpx.head(json_url, timeout=10.0, follow_redirects=True)
                server_last_modified = head_response.headers.get("Last-Modified")

                if server_last_modified:
                    server_date = parsedate_to_datetime(server_last_modified)
                    local_date_str = meta.get("downloaded_at")

                    if local_date_str:
                        local_date = datetime.fromisoformat(local_date_str)

                        if server_date.replace(tzinfo=None) > local_date:
                            updates_available.append(
                                {
                                    "name": name,
                                    "local_date": local_date.strftime("%Y-%m-%d %H:%M"),
                                    "server_date": server_date.strftime("%Y-%m-%d %H:%M"),
                                    "age_days": (datetime.now() - local_date).days,
                                }
                            )
                            print(f"🔄 {name}: mise a jour disponible")
                            print(f"   Local:  {local_date.strftime('%Y-%m-%d %H:%M')}")
                            print(f"   Serveur: {server_date.strftime('%Y-%m-%d %H:%M')}\n")
                        else:
                            print(f"✅ {name}: a jour")

            except Exception as e:
                print(f"⚠️  {name}: erreur - {e}")

        print("\n📊 Resume:")
        print(f"   Verifies: {checked}")
        print(f"   Mises a jour disponibles: {len(updates_available)}")

        return updates_available


def download_mos_terminologies(
    force: bool = False, include: Optional[list[str]] = None, exclude: Optional[list[str]] = None
) -> dict[str, int]:
    """
    Fonction helper pour telecharger les referentiels MOS/NOS.

    Args:
        force: Force le telechargement meme si deja a jour
        include: Patterns a inclure (ex: ["TRE_R*"])
        exclude: Patterns a exclure

    Returns:
        Statistiques de telechargement

    Example:
        >>> from annuairesante.mos.downloader import download_mos_terminologies
        >>>
        >>> # Telecharger tous les TRE
        >>> stats = download_mos_terminologies(include=["TRE_*"])
        >>>
        >>> # Telecharger tous sauf les ASS
        >>> stats = download_mos_terminologies(exclude=["ASS_*"])
    """
    downloader = MOSDownloader()
    stats = downloader.download_all(force=force, include_patterns=include, exclude_patterns=exclude)

    # Construire l'index apres telechargement
    if stats["downloaded"] > 0:
        downloader.build_lookup_index()

    return stats
