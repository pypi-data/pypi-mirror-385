"""
Generateur LaTeX pour la classe amsart (American Mathematical Society)
"""

from .base import BaseGenerator


class AMSGenerator(BaseGenerator):
    """Generateur pour la classe amsart utilisant Jinja2"""

    DOCUMENT_CLASS = "amsart"
