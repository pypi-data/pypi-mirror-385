"""
Generateur LaTeX pour la classe siamart (SIAM)
"""

from .base import BaseGenerator


class SIAMGenerator(BaseGenerator):
    """Generateur pour la classe siamart utilisant Jinja2"""

    DOCUMENT_CLASS = "siamart"
