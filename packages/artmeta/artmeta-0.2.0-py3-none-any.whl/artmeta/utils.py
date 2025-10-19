"""
Fonctions utilitaires pour artmeta
"""

import re
from datetime import datetime
from pathlib import Path


def insert_in_tex(tex_file: str, latex_code: str, journal_class: str) -> None:
    """
    Insère ou met à jour le code LaTeX entre balises dans un fichier .tex.

    Les balises utilisées sont de la forme:
    % BEGIN AUTO-GENERATED [journal_class]
    ...
    % END AUTO-GENERATED [journal_class]

    Args:
        tex_file: Chemin vers le fichier .tex
        latex_code: Code LaTeX à insérer
        journal_class: Nom de la classe de journal (pour les balises)

    Raises:
        FileNotFoundError: Si le fichier .tex n'existe pas
    """
    begin_tag = f"% BEGIN AUTO-GENERATED [{journal_class}]"
    end_tag = f"% END AUTO-GENERATED [{journal_class}]"

    new_block = f"{begin_tag}\n{latex_code}\n{end_tag}"

    tex_path = Path(tex_file)

    if not tex_path.exists():
        raise FileNotFoundError(f"{tex_file} introuvable")

    content = tex_path.read_text(encoding="utf-8")

    # Remplacer la classe de document
    docclass_pattern = r"\\documentclass\[?.*?]?\{(.*?)}"
    match = re.search(docclass_pattern, content)
    if match:
        old_class = match.group(1)
        if old_class != journal_class:
            new_docclass_line = match.group(0).replace(old_class, journal_class)
            content = content.replace(match.group(0), new_docclass_line)
            print(f"✓ Classe de document changée de '{old_class}' à '{journal_class}'")

    pattern = f"{re.escape(begin_tag)}.*?{re.escape(end_tag)}"

    if re.search(pattern, content, re.DOTALL):
        # Mise à jour d'un bloc existant
        new_content = re.sub(pattern, new_block, content, flags=re.DOTALL)
        action = "✓ Mise à jour"
    else:
        # Insertion d'un nouveau bloc
        if "\\begin{document}" in content:
            new_content = content.replace(
                "\\begin{document}", f"{new_block}\n\n\\begin{{document}}"
            )
        else:
            new_content = new_block + "\n\n" + content
        action = "✓ Insertion"

    tex_path.write_text(new_content, encoding="utf-8")
    print(f"{action} du bloc [{journal_class}] dans {tex_file}")


def generate_yaml_template() -> str:
    """
    Génère un template YAML pour art.yml.

    Returns:
        Contenu du template YAML
    """
    template = """# Métadonnées de l'article
# Généré le {date}

title: "Titre de l'article"
title_short: ""  # Optionnel, pour running head

authors:
  - firstname: "Prénom"
    lastname: "Nom"
    email: "prenom.nom@institution.fr"
    orcid: "0000-0000-0000-0000"  # Optionnel
    affiliations: [1]
    corresponding: true  # Un seul auteur correspondant

  # - firstname: "Prénom2"
  #   lastname: "Nom2"
  #   email: "prenom2.nom2@institution.fr"
  #   orcid: "0000-0000-0000-0001"
  #   affiliations: [2]

affiliations:
  - id: 1
    name: "Nom du laboratoire"
    name_short: "Acronyme"  # Optionnel
    umr: "UMR 1234"  # Optionnel
    institution: "Université X"
    city: "Ville"
    country: "France"

  # - id: 2
  #   name: "Autre laboratoire"
  #   institution: "Institution Y"
  #   city: "Ville"
  #   country: "Pays"

abstract: |
  Résumé de l'article en plusieurs lignes.

  Peut contenir plusieurs paragraphes.

keywords:
  - "mot-clé 1"
  - "mot-clé 2"
  - "mot-clé 3"

msc_codes:
  - "35K15"  # Code MSC principal
  - "65M12"  # Code MSC secondaire

# Métadonnées administratives
funding: "ANR-XX-CEXXX-0000 (Nom du projet)"  # Optionnel
date_submitted: "{date}"
date_revised: null
date_accepted: null

# Configuration HAL (pour dépôt automatisé)
hal:
  document_type: "PREPRINT"  # ou "ART" après acceptation
  language: "en"  # ou "fr"
  domains:
    - "math.AP"  # Domaine HAL principal
    - "math.NA"  # Domaine HAL secondaire
  license: "CC-BY-4.0"
  propagate_arxiv: true
  arxiv_category: "math.NA"
  comment: "XX pages, Y figures"  # Apparaît sur ArXiv
""".format(
        date=datetime.now().strftime("%Y-%m-%d")
    )

    return template


def get_stats(meta: dict) -> dict:
    """
    Calcule des statistiques sur les métadonnées.

    Args:
        meta: Dictionnaire des métadonnées

    Returns:
        Dictionnaire avec les statistiques
    """
    stats = {}

    # Longueur abstract
    if "abstract" in meta:
        abstract = meta["abstract"]
        stats["abstract_words"] = len(abstract.split())
        stats["abstract_chars"] = len(abstract)

    # Nombre d'auteurs
    if "authors" in meta:
        stats["authors_count"] = len(meta["authors"])
        stats["authors_with_orcid"] = sum(1 for a in meta["authors"] if "orcid" in a)

    # Nombre d'affiliations
    if "affiliations" in meta:
        stats["affiliations_count"] = len(meta["affiliations"])

    # Pays représentés
    if "affiliations" in meta:
        countries = set(a.get("country", "Inconnu") for a in meta["affiliations"])
        stats["countries"] = sorted(countries)

    # Nombre de mots-clés et MSC
    if "keywords" in meta:
        stats["keywords_count"] = len(meta["keywords"])

    if "msc_codes" in meta:
        stats["msc_codes_count"] = len(meta["msc_codes"])

    return stats
