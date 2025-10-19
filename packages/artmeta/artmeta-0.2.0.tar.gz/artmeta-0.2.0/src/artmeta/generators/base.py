"""
Classe de base abstraite pour les générateurs LaTeX
"""

import re
from abc import ABC
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader


class BaseGenerator(ABC):
    """Classe de base pour tous les générateurs LaTeX"""

    # Nom de la classe LaTeX (à surcharger dans les sous-classes)
    DOCUMENT_CLASS: str = ""

    def __init__(self, metadata: Dict[str, Any]):
        """
        Initialise le générateur avec les métadonnées.

        Args:
            metadata: Dictionnaire des métadonnées de l'article
        """
        self.meta = metadata
        self._setup_jinja()

    def _setup_jinja(self):
        """Configure l'environnement Jinja2"""
        templates_dir = Path(__file__).parent.parent / "templates"

        # Fonction personnalisée pour détecter l'autoescape
        def should_autoescape(template_name):
            if template_name is None:
                return False
            # Activer l'autoescape XML pour les templates .xml.j2
            return template_name.endswith(".xml.j2")

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=should_autoescape,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Ajouter des filtres personnalisés pour LaTeX
        self.jinja_env.filters["latex_escape"] = self._latex_escape

    @staticmethod
    def _latex_escape(text: str) -> str:
        """
        Échappe les caractères spéciaux LaTeX.

        Args:
            text: Texte à échapper

        Returns:
            Texte échappé pour LaTeX
        """
        if not isinstance(text, str):
            return text

        # Utiliser une regex pour faire tous les remplacements en une seule passe
        # Cela évite que les caractères ajoutés par un remplacement soient
        # eux-mêmes remplacés par les remplacements suivants
        replacements = {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }

        # Créer un pattern avec toutes les clés, en échappant les caractères spéciaux regex
        # IMPORTANT: \ doit être en premier dans le pattern
        pattern = re.compile("|".join(re.escape(key) for key in replacements.keys()))

        def replace_func(match):
            return replacements[match.group(0)]

        return pattern.sub(replace_func, text)

    def _format_author_name(self, author: Dict[str, str]) -> str:
        """
        Formate le nom d'un auteur selon les conventions de la classe.

        Args:
            author: Dictionnaire avec firstname, lastname, etc.

        Returns:
            Nom formaté (à surcharger si besoin)
        """
        firstname = author.get("firstname", "")
        lastname = author.get("lastname", "")
        return f"{firstname} {lastname}"

    def _get_template_name(self) -> str:
        """
        Retourne le nom du template Jinja2 à utiliser.

        Returns:
            Nom du fichier template (ex: 'amsart.tex.j2')
        """
        return f"{self.DOCUMENT_CLASS}.tex.j2"

    def generate(self) -> str:
        """
        Génère le code LaTeX pour la classe de document.

        Par défaut, utilise un template Jinja2 basé sur DOCUMENT_CLASS.
        Les sous-classes peuvent surcharger cette méthode si nécessaire.

        Returns:
            Code LaTeX généré
        """
        return self.generate_with_template()

    def generate_with_template(self, template_name: Optional[str] = None) -> str:
        """
        Génère le code LaTeX en utilisant un template Jinja2.

        Args:
            template_name: Nom du template (si None, utilise _get_template_name())

        Returns:
            Code LaTeX généré
        """
        if template_name is None:
            template_name = self._get_template_name()

        template = self.jinja_env.get_template(template_name)

        # Préparer le contexte pour le template
        context = {"meta": self.meta, "affiliations": self.get_affiliations_map()}

        return template.render(**context)

    def get_affiliations_map(self) -> Dict[int, Dict[str, Any]]:
        """
        Retourne un dictionnaire {id: affiliation} pour accès rapide.

        Returns:
            Dictionnaire avec les IDs d'affiliation comme clés
        """
        if "affiliations" not in self.meta:
            return {}

        return {affil["id"]: affil for affil in self.meta["affiliations"]}
