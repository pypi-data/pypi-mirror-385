"""
Validation des métadonnées pour artmeta
"""

import re
from typing import Any, Dict, List, Tuple


def validate_metadata(meta: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Valide la structure et le contenu des métadonnées.

    Args:
        meta: Dictionnaire des métadonnées chargées depuis YAML

    Returns:
        Tuple (errors, warnings) avec les listes d'erreurs et d'avertissements
    """
    errors = []
    warnings = []

    # Champs obligatoires
    required_fields = {
        "title": "Titre de l'article",
        "authors": "Liste des auteurs",
        "abstract": "Résumé",
    }

    for field, description in required_fields.items():
        if field not in meta:
            errors.append(f"Champ obligatoire manquant : '{field}' ({description})")

    # Validation des auteurs
    if "authors" in meta:
        author_errors, author_warnings = _validate_authors(meta)
        errors.extend(author_errors)
        warnings.extend(author_warnings)

    # Validation affiliations
    if "affiliations" in meta:
        affil_errors, affil_warnings = _validate_affiliations(meta)
        errors.extend(affil_errors)
        warnings.extend(affil_warnings)

    # Validation MSC codes
    if "msc_codes" in meta:
        msc_warnings = _validate_msc_codes(meta["msc_codes"])
        warnings.extend(msc_warnings)

    return errors, warnings


def _validate_authors(meta: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Valide les auteurs"""
    errors = []
    warnings = []

    for i, author in enumerate(meta["authors"], 1):
        author_required = ["firstname", "lastname", "email"]
        for field in author_required:
            if field not in author:
                errors.append(f"Auteur {i} : champ '{field}' manquant")

        # Validation email
        if "email" in author:
            if not validate_email(author["email"]):
                warnings.append(f"Auteur {i} : format email suspect '{author['email']}'")

        # Validation ORCID
        if "orcid" in author:
            if not validate_orcid(author["orcid"]):
                errors.append(
                    f"Auteur {i} : format ORCID invalide '{author['orcid']}' "
                    f"(attendu : 0000-0000-0000-0000)"
                )

        # Validation affiliations
        if "affiliations" in author:
            if "affiliations" not in meta:
                errors.append(f"Auteur {i} référence des affiliations mais aucune n'est définie")
            else:
                affil_ids = [a["id"] for a in meta["affiliations"]]
                for aid in author["affiliations"]:
                    if aid not in affil_ids:
                        errors.append(f"Auteur {i} : affiliation {aid} introuvable")

    return errors, warnings


def _validate_affiliations(meta: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Valide les affiliations"""
    errors = []
    warnings = []

    affil_ids = set()
    for i, affil in enumerate(meta["affiliations"], 1):
        if "id" not in affil:
            errors.append(f"Affiliation {i} : champ 'id' manquant")
        else:
            if affil["id"] in affil_ids:
                errors.append(f"Affiliation {i} : ID {affil['id']} dupliqué")
            affil_ids.add(affil["id"])

        for field in ["name", "institution", "country"]:
            if field not in affil:
                warnings.append(f"Affiliation {i} : champ '{field}' recommandé")

    return errors, warnings


def _validate_msc_codes(msc_codes: List[str]) -> List[str]:
    """Valide les codes MSC"""
    warnings = []
    msc_pattern = r"^\d{2}[A-Z]\d{2}$"

    for code in msc_codes:
        if not re.match(msc_pattern, code):
            warnings.append(f"Code MSC suspect : '{code}' (format attendu : 35K15)")

    return warnings


def validate_email(email: str) -> bool:
    """Valide le format d'un email"""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, email))


def validate_orcid(orcid: str) -> bool:
    """Valide le format d'un ORCID"""
    orcid_pattern = r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$"
    return bool(re.match(orcid_pattern, orcid))
