"""
Generateur LaTeX pour la classe article (standard LaTeX)
"""

from .base import BaseGenerator


class StandardGenerator(BaseGenerator):
    """Generateur pour la classe article standard utilisant Jinja2"""

    DOCUMENT_CLASS = "article"
