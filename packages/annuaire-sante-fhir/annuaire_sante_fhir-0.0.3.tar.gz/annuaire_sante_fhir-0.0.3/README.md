# Annuaire Santé FHIR - Client Python Moderne

[![PyPI version](https://badge.fury.io/py/annuaire-sante-fhir.svg)](https://badge.fury.io/py/annuaire-sante-fhir)
[![Python versions](https://img.shields.io/pypi/pyversions/annuaire-sante-fhir.svg)](https://pypi.org/project/annuaire-sante-fhir/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Client Python moderne et type-safe pour l'API FHIR de l'Annuaire Santé avec modèles JSON propres, sans artefacts FHIR, prêts pour injection en base de données.

## Caractéristiques

- **Modèles Pydantic v2** propres et DB-ready sans artefacts FHIR
- **Résolution automatique des codes MOS** (Modèle des Objets de Santé)
- **Transformateurs FHIR → JSON** pour chaque ressource
- **Type hints complets** pour une excellente expérience développeur
- **Support complet des profils**:
  - FR Core v2.1.0 (Practitioner, Organization, PractitionerRole, HealthcareService)
  - AS DP v1.1.0 (Annuaire Santé Données Publiques)

## Installation

```bash
pip install annuaire-sante-fhir
```

**Note**: Le nom du package sur PyPI est `annuaire-sante-fhir`, mais l'import dans votre code reste `annuairesante`:

```python
from annuairesante import AnnuaireSanteClient, transform_practitioner
```

## Configuration de la clé API

Pour utiliser l'API Annuaire Santé, vous devez obtenir une clé API :

1. **Obtenir une clé** : Rendez-vous sur [https://ansforge.github.io/annuaire-sante-fhir-documentation/pages/guide/version-2/getting-started/get-api-key.html](https://ansforge.github.io/annuaire-sante-fhir-documentation/pages/guide/version-2/getting-started/get-api-key.html) et créez un compte pour obtenir votre clé API
2. **Configurer la clé** : Trois méthodes disponibles

### Méthode 1 : Variable d'environnement (recommandé)

```bash
export ANNUAIRE_SANTE_API_KEY="votre-cle-api"
```

### Méthode 2 : Fichier .env

Créez un fichier `.env` à la racine de votre projet :

```env
ANNUAIRE_SANTE_API_KEY=votre-cle-api
```

### Méthode 3 : Paramètre direct

```python
from annuairesante import AnnuaireSanteClient

client = AnnuaireSanteClient(api_key="votre-cle-api")
```

⚠️ **Sécurité** : Ne commitez jamais votre clé API dans Git ! Ajoutez `.env` à votre `.gitignore`.

## Utilisation rapide

### Recherche simple (quelques résultats)

```python
from annuairesante import AnnuaireSanteClient, transform_practitioner

# Initialiser le client
client = AnnuaireSanteClient()  # Utilise ANNUAIRE_SANTE_API_KEY

# Rechercher des professionnels
bundle = client.practitioner.search(family="MARTIN", given="Jean")

print(f"Total trouvé: {bundle.total}")

# Parcourir les résultats
for resource in bundle.entries:
    practitioner = transform_practitioner(resource)

    print(f"Nom: {practitioner.name.full_text}")
    print(f"RPPS: {practitioner.identifiers.rpps}")

    # Exporter en JSON pour base de données
    db_ready_json = practitioner.model_dump(mode='json')
```

### Synchronisation de masse (pagination automatique)

```python
from annuairesante import AnnuaireSanteClient, transform_organization

client = AnnuaireSanteClient()

# Synchroniser toutes les organisations d'une région
count = 0
for org_fhir in client.organization.search_all(
    **{"address-postalcode": "69"},  # Département du Rhône
    active=True
):
    org = transform_organization(org_fhir)
    database.save(org.model_dump(mode='json'))

    count += 1
    if count % 100 == 0:
        print(f"{count} organisations synchronisées...")

print(f"Total: {count} organisations")
```

### Synchronisation incrémentale

```python
from annuairesante import AnnuaireSanteClient
from datetime import datetime

client = AnnuaireSanteClient()

# Synchroniser uniquement les modifications depuis la dernière synchro
last_sync = "2025-01-01T00:00:00Z"

for practitioner in client.practitioner.search_all(
    _lastUpdated=f"ge{last_sync}",  # ge = greater or equal
    **{"address-city": "Lyon"}
):
    database.upsert(practitioner)  # Mise à jour ou insertion

# Sauvegarder la date de synchro
database.set_last_sync(datetime.utcnow().isoformat() + "Z")
```

## Modèles disponibles

### Practitioner (Professionnel de santé)

```python
{
  "identifiers": {
    "idnps": "810101205564",       # Obligatoire
    "rpps": "10101205564",         # Obligatoire
    "adeli": None
  },
  "name": {
    "family": "VERDIER",
    "given": ["Pauline"],
    "prefix": "MME",               # Civilité (JDV_J78)
    "suffix": ["DR"],              # Titre exercice (JDV_J79)
    "full_text": "VERDIER Pauline"
  },
  "gender": "female",
  "birth_date": "1985-03-15",
  "contacts": {
    "phones": ["+33612345678"],
    "emails": ["contact@example.com"],
    "mssante": [{
      "email": "pauline.verdier@aura.mssante.fr",
      "type": "PER",               # ORG, APP, PER, CAB
      "digitization": false,
      "liste_rouge": false
    }]
  },
  "addresses": [{
    "lines": ["2 RUE CLAUDE BERNARD"],
    "city": "PARIS",
    "postal_code": "75005",
    "insee_code": "75105"
  }],
  "qualifications": {              # Indexé par type puis nom de système
    "profession": {
      "ProfessionSante": {
        "code": "21",
        "display": "Médecin"       # Résolu via MOS
      },
      "CategorieProfessionnelle": {
        "code": "C",
        "display": "Civil"
      }
    },
    "diplome": {
      "DiplomeEtatFrancais": {
        "code": "DE28",
        "display": "DE Docteur en médecine"
      }
    }
  },
  "smartcards": [{
    "type": "CPS",
    "number": "3100434368",
    "period": {"start": "2024-02-21", "end": "2027-02-21"},
    "is_valid": true
  }],
  "metadata": {
    "id": "003-3014698-3057235",
    "version_id": "1",
    "last_updated": "2025-04-28T18:19:26.335+02:00",
    "profiles": ["https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-practitioner"],
    "data_trace": {
      "systeme_information": "RPPS"
    }
  },
  "active": true
}
```

### Organization (Structure de santé)

```python
{
  "identifiers": {
    "finess": "750010753",         # FINEJ ou FINEG
    "idnst": "1750010753",
    "siret": "12345678901234"
  },
  "name": "PHARMACIE BLONDEEL",
  "aliases": ["LA GRANDE PHARMACIE DU 5"],
  "types_by_category": {            # Indexé par catégorie
    "categorieEtablissement": {
      "code": "620",
      "display": "Pharmacie d'officine",  # Résolu via MOS
      "category": "categorieEtablissement"
    },
    "secteurActiviteRASS": {
      "code": "SA33",
      "display": "Secteur privé commercial",
      "category": "secteurActiviteRASS"
    },
    "statutJuridiqueINSEE": {
      "code": "101",
      "display": "SELAS",
      "category": "statutJuridiqueINSEE"
    }
  },
  "primary_type": {                 # Type sans catégorie spécifique
    "code": "620",
    "display": "Pharmacie d'Officine",
    "category": null
  },
  "pharmacy_licence": "75#000283",
  "addresses": [...]
}
```

### Autres ressources

- **PractitionerRole**: Situation d'exercice (genre, mode, fonction)
- **HealthcareService**: Service/activité de santé (modalité, type, forme)
- **Device**: Équipement matériel lourd

## Accès simplifié aux données

Les structures JSON sont optimisées pour un accès direct sans boucles :

```python
# Practitioner - Accès aux qualifications
pract.qualifications["profession"]["ProfessionSante"]
# → {"code": "21", "display": "Pharmacien"}

# Helpers disponibles
pract.get_profession()  # Code profession principal
pract.get_diploma()     # Diplôme principal
pract.get_category()    # Catégorie professionnelle

# Organization - Accès aux types
org.types_by_category["secteurActiviteRASS"]
# → {"code": "SA33", "display": "Pharmacie d'officine"}

org.primary_type        # Type principal (sans catégorie)

# Helpers disponibles
org.get_secteur_activite()
org.get_statut_juridique()
```

**Note** : Les clés des dictionnaires sont des **noms lisibles** ("ProfessionSante", "DiplomeEtatFrancais") extraits des référentiels MOS. Si l'index MOS n'est pas encore construit avec le nouveau format, les codes de table sont utilisés comme fallback ("TRE-G15", "TRE-R48").

Pour construire l'index avec les noms lisibles :
```bash
python examples/update_mos_cache.py
```

## Résolution MOS

Tous les codes MOS (TRE_*, JDV_*) sont automatiquement résolus en libellés lisibles :

```python
from annuairesante.mos import MOSResolver

resolver = MOSResolver()
display = resolver.resolve(
    "https://mos.esante.gouv.fr/NOS/TRE_G15-ProfessionSante/FHIR/TRE-G15-ProfessionSante",
    "21"
)
# → "Médecin"
```

## API et ressources disponibles

### Ressources FHIR supportées

| Ressource | Description | Exemples |
|-----------|-------------|----------|
| **Practitioner** | Professionnels de santé | `client.practitioner.search(family="MARTIN")` |
| **Organization** | Structures de santé | `client.organization.search(type="620")` |
| **PractitionerRole** | Situations d'exercice | `client.practitioner_role.search(practitioner="003-123456")` |
| **HealthcareService** | Services/activités de santé | `client.healthcare_service.search(organization="001-01-174986")` |
| **Device** | Équipements matériels lourds | `client.device.search(type="05602")` |

### Méthodes disponibles

Pour chaque ressource, trois méthodes sont disponibles :

```python
# 1. search() - Recherche avec résultat paginé (Bundle)
bundle = client.practitioner.search(family="MARTIN", _count=20)
print(f"Page courante: {len(bundle.entries)} résultats")
# Note: bundle.total est toujours 0 (l'API ne fournit pas ce champ)
for entry in bundle.entries:
    process(entry)

# Pagination manuelle
while bundle.has_next():
    bundle = bundle.next()
    for entry in bundle.entries:
        process(entry)

# 2. search_all() - Générateur avec pagination automatique
for practitioner in client.practitioner.search_all(family="MARTIN"):
    database.save(practitioner)

# 3. get() - Récupérer par ID
practitioner = client.practitioner.get("003-123456")
```

### Paramètres de recherche

Consultez la [documentation complète des paramètres](docs/API_PARAMETERS.md) pour la liste exhaustive.

**Exemples courants :**

```python
# Practitioner
client.practitioner.search(
    family="MARTIN",                    # Nom de famille
    given="Jean",                       # Prénom
    **{"qualification-code": "10"},     # Code profession (10=Médecin dans TRE-G15)
    **{"mailbox-mss": "jean@mssante.fr"}, # Boîte MSS
    active=True,                        # Actif uniquement
    _lastUpdated="ge2025-01-01"         # Modifié depuis le 1er janvier
)

# Organization
client.organization.search(
    name="hopital",                     # Nom (recherche partielle)
    identifier="750010753",             # FINESS, SIRET, etc.
    type="620",                         # Type (620 = Pharmacie)
    **{"address-city": "Paris"},        # Ville
    **{"address-postalcode": "75"},     # Code postal / département
    active=True
)

# PractitionerRole
client.practitioner_role.search(
    practitioner="003-123456",          # ID du professionnel
    organization="001-01-879996",       # ID de l'organisation
    role="204",                         # Code fonction/activité
    active=True
)
```

## Exemples complets

### 1. Recherche et affichage

```python
from annuairesante import AnnuaireSanteClient, transform_practitioner

client = AnnuaireSanteClient()

# Rechercher des médecins à Lyon
bundle = client.practitioner.search(
    **{"qualification-code": "10"},  # Médecin (code TRE-G15)
    _count=10
)

print(f"Médecins (page courante): {len(bundle.entries)} résultats")

for resource in bundle.entries:
    practitioner = transform_practitioner(resource)

    print(f"\n{practitioner.name.full_text}")
    print(f"  RPPS: {practitioner.identifiers.rpps}")

    if practitioner.contacts.mssante:
        print(f"  MSSanté: {practitioner.contacts.mssante[0].email}")
```

### 2. Synchronisation régionale complète

```python
from annuairesante import AnnuaireSanteClient, transform_organization
import json

client = AnnuaireSanteClient()

# Exporter toutes les pharmacies du département 69 en JSON Lines
with open("pharmacies_69.jsonl", "w") as f:
    for org_fhir in client.organization.search_all(
        type="620",                             # Pharmacie d'officine
        **{"address-postalcode": "69"},         # Rhône
        active=True,
        _count=100                              # 100 par page
    ):
        org = transform_organization(org_fhir)
        json.dump(org.model_dump(mode='json'), f, ensure_ascii=False)
        f.write("\n")
```

### 3. Mise à jour incrémentale quotidienne

```python
from annuairesante import AnnuaireSanteClient
from datetime import datetime

client = AnnuaireSanteClient()

# Lire la dernière date de synchro
last_sync = load_last_sync_date()  # Ex: "2025-10-08T00:00:00Z"

# Synchroniser uniquement les modifications
modified_count = 0
for org in client.organization.search_all(
    _lastUpdated=f"ge{last_sync}",
    **{"address-postalcode": "69"}
):
    database.upsert(org)
    modified_count += 1

# Sauvegarder la nouvelle date
save_last_sync_date(datetime.utcnow().isoformat() + "Z")
print(f"{modified_count} organisations mises à jour")
```

Voir aussi les exemples complets dans le dossier [`examples/`](examples/) :
- `basic_usage.py` - Utilisation basique
- `api_search.py` - Recherches avancées et pagination
- `sync_region.py` - Synchronisation de masse d'une région
- `incremental_sync.py` - Synchronisation incrémentale avec gestion d'état

## Développement

```bash
# Installer en mode développement
pip install -e ".[dev]"

# Tests
pytest

# Formatage
black src/
ruff check src/

# Type checking
mypy src/
```

## Standards et conformité

Cette bibliothèque implémente:

- **FR Core v2.1.0**: Profils FHIR français (HL7 France)
  - FR Core Practitioner
  - FR Core Organization
  - FR Core PractitionerRole
  - FR Core HealthcareService
  - FR Core Address, ContactPoint, HumanName

- **AS DP v1.1.0**: Profils Annuaire Santé Données Publiques
  - AS DP Practitioner (extensions: smartcard, mailbox-mss-metadata)
  - AS DP Organization (extensions: organization-types, pharmacy-licence)
  - AS DP PractitionerRole
  - AS DP HealthcareService Healthcare Activity (extension: authorization)
  - AS DP Device (extension: authorization)

## Licence

MIT

## Contributions

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.
