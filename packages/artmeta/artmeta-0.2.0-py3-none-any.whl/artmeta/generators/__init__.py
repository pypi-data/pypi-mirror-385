"""
Generateurs LaTeX pour differentes classes de revues
"""

from typing import Any, Dict

from .ams import AMSGenerator
from .elsevier import ElsevierGenerator
from .hal import HALGenerator
from .siam import SIAMGenerator
from .springer import SpringerGenerator
from .standard import StandardGenerator

__all__ = [
    "AMSGenerator",
    "ElsevierGenerator",
    "SpringerGenerator",
    "SIAMGenerator",
    "StandardGenerator",
    "HALGenerator",
    "get_generator",
]

# Mapping des classes de journal vers leurs generateurs
GENERATORS = {
    "amsart": AMSGenerator,
    "elsarticle": ElsevierGenerator,
    "svjour3": SpringerGenerator,
    "siamart": SIAMGenerator,
    "article": StandardGenerator,
    "hal": HALGenerator,
}


def get_generator(journal_class: str, metadata: Dict[str, Any]):
    """
    Retourne le generateur approprie pour une classe de journal.

    Args:
        journal_class: Nom de la classe LaTeX (amsart, elsarticle, etc.)
        metadata: Dictionnaire des metadonnees

    Returns:
        Instance du generateur approprie

    Raises:
        ValueError: Si la classe de journal n'est pas supportee
    """
    if journal_class not in GENERATORS:
        available = ", ".join(GENERATORS.keys())
        raise ValueError(f"Classe '{journal_class}' inconnue. Disponibles : {available}")

    generator_class = GENERATORS[journal_class]
    return generator_class(metadata)
