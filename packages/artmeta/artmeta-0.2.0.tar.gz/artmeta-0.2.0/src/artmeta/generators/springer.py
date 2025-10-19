"""
Generateur LaTeX pour la classe svjour3 (Springer)
"""

from .base import BaseGenerator


class SpringerGenerator(BaseGenerator):
    """Generateur pour la classe svjour3 utilisant Jinja2"""

    DOCUMENT_CLASS = "svjour3"
