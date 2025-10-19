"""
Générateur HAL-XML pour dépôt sur HAL
"""

from .base import BaseGenerator


class HALGenerator(BaseGenerator):
    """Générateur pour le format HAL-XML"""

    DOCUMENT_CLASS = "hal"

    def generate_xml(self) -> str:
        """
        Génère le fichier HAL-XML complet.

        Returns:
            Contenu XML formaté pour HAL
        """
        return self.generate_with_template("hal.xml.j2")
