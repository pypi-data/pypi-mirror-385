"""
Point d'entrée pour l'exécution en tant que module Python
Permet d'exécuter : python -m artmeta
"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
