"""
artmeta - Gestionnaire de metadonnees pour articles academiques

Ce package permet de gerer les metadonnees d'articles scientifiques,
de generer du code LaTeX pour differentes classes de revues,
et d'exporter vers HAL et ArXiv.
"""

from .cli import main
from .core import ArtMeta

__version__ = "0.1.0"

__all__ = ["ArtMeta", "main", "__version__"]
