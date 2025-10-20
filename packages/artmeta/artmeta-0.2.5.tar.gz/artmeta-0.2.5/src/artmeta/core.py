"""
Classe principale pour la gestion des métadonnées
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .validators import validate_metadata


class ArtMeta:
    """Classe principale pour la gestion des métadonnées d'articles académiques"""

    def __init__(self, metadata_file: str = "art.yml"):
        """
        Initialise ArtMeta avec un fichier de métadonnées.

        Args:
            metadata_file: Chemin vers le fichier YAML de métadonnées
        """
        self.metadata_file = Path(metadata_file)
        self.meta: Optional[Dict[str, Any]] = None

        if self.metadata_file.exists():
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                self.meta = yaml.safe_load(f)

    def validate(self) -> Tuple[List[str], List[str]]:
        """
        Valide la structure et le contenu de art.yml.

        Returns:
            Tuple (errors, warnings) avec les listes d'erreurs et d'avertissements

        Raises:
            FileNotFoundError: Si le fichier de métadonnées n'existe pas
        """
        if not self.metadata_file.exists():
            raise FileNotFoundError(f"{self.metadata_file} introuvable")

        if self.meta is None:
            raise ValueError(f"Métadonnées non chargées depuis {self.metadata_file}")

        return validate_metadata(self.meta)

    def get_authors_count(self) -> int:
        """Retourne le nombre d'auteurs"""
        if self.meta and "authors" in self.meta:
            return len(self.meta["authors"])
        return 0

    def get_corresponding_author(self) -> Optional[Dict[str, Any]]:
        """Retourne l'auteur correspondant (si défini)"""
        if self.meta and "authors" in self.meta:
            for author in self.meta["authors"]:
                if author.get("corresponding", False):
                    return author
        return None

    def get_affiliations_map(self) -> Dict[int, Dict[str, Any]]:
        """
        Retourne un dictionnaire {id: affiliation} pour accès rapide.

        Returns:
            Dictionnaire avec les IDs d'affiliation comme clés
        """
        if not self.meta or "affiliations" not in self.meta:
            return {}

        return {affil["id"]: affil for affil in self.meta["affiliations"]}

    def get_title(self, short: bool = False) -> str:
        """
        Retourne le titre de l'article.

        Args:
            short: Si True, retourne le titre court (si disponible)

        Returns:
            Le titre de l'article
        """
        if not self.meta:
            return ""

        if short and "title_short" in self.meta and self.meta["title_short"]:
            return self.meta["title_short"]

        return self.meta.get("title", "")
