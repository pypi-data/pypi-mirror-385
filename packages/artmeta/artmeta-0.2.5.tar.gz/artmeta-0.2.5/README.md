# artmeta

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![pipeline status](https://plmlab.math.cnrs.fr/nicolas.klutchnikoff/artmeta/badges/main/pipeline.svg)](https://plmlab.math.cnrs.fr/nicolas.klutchnikoff/artmeta/-/pipelines)
[![coverage report](https://plmlab.math.cnrs.fr/nicolas.klutchnikoff/artmeta/badges/main/coverage.svg)](https://plmlab.math.cnrs.fr/nicolas.klutchnikoff/artmeta/-/pipelines)
[![PyPI version](https://badge.fury.io/py/artmeta.svg)](https://badge.fury.io/py/artmeta) <!-- Placeholder : à activer lors de la publication sur PyPI -->
[![Documentation Status](https://readthedocs.org/projects/artmeta/badge/?version=latest)](https://artmeta.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Gérez les métadonnées de vos articles scientifiques sans effort.**

`artmeta` est un outil en ligne de commande qui vous libère de la gestion fastidieuse des métadonnées d'articles. Définissez auteurs, affiliations et résumé une seule fois dans un fichier YAML, et laissez `artmeta` générer le code LaTeX pour n'importe quelle revue.

### Concept

```
[ art.yml ] ----( artmeta )----> [ Code LaTeX / HAL XML ]
```

---

### Installation

```bash
pip install artmeta
```

### Exemple d'Utilisation

```bash
# 1. Initialisez votre fichier de métadonnées
artmeta init

# 2. Générez et insérez le code pour une revue (ex: AMS)
artmeta generate -j amsart --insert main.tex

# 3. Rejeté ? Changez de revue en une seule commande
artmeta switch -j elsarticle main.tex
```

---

### 📖 Documentation

Pour un guide complet, des exemples et des tutoriels, **[consultez la documentation](https://artmeta.readthedocs.io)**.

### 🤝 Contribuer

Les contributions sont les bienvenues ! Voir le **[guide de contribution](https://artmeta.readthedocs.io/en/latest/contributing/)**.

### 📄 Licence

Ce projet est sous licence [MIT](LICENSE).