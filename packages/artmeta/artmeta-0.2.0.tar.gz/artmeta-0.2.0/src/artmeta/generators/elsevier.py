"""
Generateur LaTeX pour la classe elsarticle (Elsevier)
"""

from .base import BaseGenerator


class ElsevierGenerator(BaseGenerator):
    """Generateur pour la classe elsarticle utilisant Jinja2"""

    DOCUMENT_CLASS = "elsarticle"
