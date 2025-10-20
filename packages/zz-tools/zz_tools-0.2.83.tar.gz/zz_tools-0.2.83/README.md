<!-- BEGIN BADGES -->
[![Docs](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/docs.yml/badge.svg)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/docs.yml)
[![CodeQL](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/codeql.yml/badge.svg)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/codeql.yml)
[![Release](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/release-publish.yml/badge.svg)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/release-publish.yml)
[![CI accel](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-accel.yml/badge.svg)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-accel.yml)
<!-- END BADGES -->

[![ci-pre-commit](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-pre-commit.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-pre-commit.yml)
[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
# Modèle de Courbure Gravitationnelle Temporelle (MCGT)
## Résumé
MCGT est un corpus structuré en chapitres, accompagné de scripts, données, figures et manifestes assurant la reproductibilité.


### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
 chapitres (conceptuel + détails) accompagné d’un ensemble de scripts, données, figures et manifestes pour assurer la reproductibilité complète (génération des données, tracés, contrôles de cohérence). Ce README dresse l’index des ressources, précise les points d’entrée (runbook, Makefile, configs) et documente les conventions.
## Sommaire
1. Arborescence du projet
2. Contenu des chapitres (LaTeX)
3. Configurations & package Python
4. Données (zz-data/)
5. Scripts (zz-scripts/)
6. Figures (zz-figures/)
7. Manifests & repro (zz-manifests/, README-REPRO.md, RUNBOOK.md)
8. Conventions & styles (conventions.md)
9. Environnements & dépendances (requirements.txt, environment.yml)

## 1) Arborescence du projet
Racine :
* main.tex — Document LaTeX principal.

## 2) Contenu des chapitres (LaTeX)
Chaque dossier de chapitre contient :
* <prefix>\_conceptuel.tex
* <prefix>\_details.tex (ou \_calibration\_conceptuel.tex pour le chap. 1)
* CHAPTERXX\_GUIDE.txt (notes, exigences, jalons spécifiques)
* Chapitre 1 – Introduction conceptuelle

## 3) Configurations & package Python
* zz-configuration/mcgt-global-config.ini : paramètres transverses (chemins de données/figures, tolérances, seeds, options graphiques, etc.).
* zz-configuration/\*.ini spécifiques (ex. camb\_exact\_plateau.ini, scalar\_perturbations.ini, gw\_phase.ini).
* zz-configuration/GWTC-3-confident-events.json ; zz-configuration/pdot\_plateau\_vs\_z.dat ; zz-configuration/meta\_template.json ; zz-configuration/mcgt-global-config.ini.template ; zz-configuration/README.md.
* mcgt/ : API Python interne (ex. calculs de phase, solveurs de perturbations, backends de référence). mcgt/backends/ref\_phase.py fournit la phase de ref.
* mcgt/CHANGELOG.md ; mcgt/pyproject.toml.
---
## 4) Données (zz-data/)
Organisation par chapitre, exemples (liste non exhaustive) :
* zz-data/chapter…

## 5) Scripts (zz-scripts/)
Chaque chapitre dispose de générateurs de données generate\_data\_chapterXX.py et de traceurs plot\_fig\*.py. Exemples :
* zz-scripts/chapter…

## 6) Figures (zz-figures/)
Par chapitre : fig\_\*.png (noms explicites, FR).
* chapitres

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->1 :
  * fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->1\_early\_plateau.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->2\_logistic\_calibration.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_relative\_error\_timeline.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->4\_P\_vs\_T\_evolution.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->5\_I1\_vs\_T.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->6\_P\_derivative\_comparison.png
* chap.<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->2 :
  * fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END --><!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->\_spectrum.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->1\_P\_vs\_T\_evolution.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->2\_calibration.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_relative\_errors.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->4\_pipeline\_diagram.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->5\_FG\_series.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->6\_fit\_alpha.png
* chap.<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3 :
  * fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->1\_fR\_stability\_domain.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->2\_fR\_fRR\_vs\_R.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_ms2\_R<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->\_vs\_R.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->4\_fR\_fRR\_vs\_R.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->5\_interpolated\_milestones.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->6\_grid\_quality.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->7\_ricci\_fR\_vs\_z.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->8\_ricci\_fR\_vs\_T.png
* chap.<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->4 :
  * fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->1\_invariants\_schematic.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->2\_invariants\_histogram.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_invariants\_vs\_T.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->4\_relative\_deviations.png
* chap.<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->5 :
  * fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->1\_bbn\_reaction\_network.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->2\_dh\_model\_vs\_obs.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_yp\_model\_vs\_obs.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->4\_chi2\_vs\_T.png
* chap.<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->6 :
  * fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->1\_cmb\_dataflow\_diagram.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->2\_cls\_lcdm\_vs\_mcgt.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_delta\_cls\_relative.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->4\_delta\_rs\_vs\_params.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->5\_delta\_chi2\_heatmap.png
* chap.<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->7 :
  * fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END --><!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->\_loglog\_sampling\_test.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->1\_cs2\_heatmap\_k\_a.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->2\_delta\_phi\_heatmap\_k\_a.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_invariant\_I1.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->4\_dcs2\_dk\_vs\_k.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->5\_ddelta\_phi\_dk\_vs\_k.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->6\_comparison.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->7\_invariant\_I2.png
* chap.<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->8 :
  * fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->1\_chi2\_total\_vs\_q<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->2\_dv\_vs\_z.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_mu\_vs\_z.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->4\_chi2\_heatmap.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->5\_residuals.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->6\_pulls.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->7\_chi2\_profile.png
* chap.<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->9 :
  * fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->1\_phase\_overlay.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->2\_residual\_phase.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_hist\_absdphi\_2<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->\_3<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END --><!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->4\_absdphi\_milestones\_vs\_f.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->5\_scatter\_phi\_at\_fpeak.png, p95\_methods/ (fig<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_raw\_bins3<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->.png, fig<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_raw\_bins5<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->.png, fig<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_raw\_bins8<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->.png, fig<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_rebranch\_k\_bins3<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->.png, fig<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_rebranch\_k\_bins5<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->.png, fig<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_rebranch\_k\_bins8<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->.png, fig<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_unwrap\_bins3<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->.png, fig<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_unwrap\_bins5<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->.png, fig<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_unwrap\_bins8<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->.png), p95\_check\_control.png
* chap.1<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END --> :
  * fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->1\_iso\_p95\_maps.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->2\_scatter\_phi\_at\_fpeak.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3b\_coverage\_bootstrap\_vs\_n\_hires.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->3\_convergence\_p95\_vs\_n.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->4\_scatter\_p95\_recalc\_vs\_orig.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->5\_hist\_cdf\_metrics.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->6\_heatmap\_absdp95\_m1m2.png, fig\_<!-- CI:BEGIN -->
### CI (Workflows canoniques)

[![sanity-main](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-main.yml)
[![sanity-echo](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/sanity-echo.yml)
[![ci-yaml-check](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml/badge.svg?branch=main)](https://github.com/JeanPhilipLalumiere/MCGT/actions/workflows/ci-yaml-check.yml)

- **sanity-main.yml** : diag quotidien / dispatch / push (artefacts)
- **sanity-echo.yml** : smoke déclenchable manuellement
- **ci-yaml-check.yml** : lint/validité YAML

Voir `docs/CI.md`.
<!-- CI:END -->7\_summary\_comparison.png
---
## 7) Manifests & repro
* zz-manifests/manifest\_master.json — inventaire complet (source maître).
* zz-manifests/manifest\_publication.json — sous-ensemble pour remise publique.
* zz-manifests/manifest\_report.json — rapport généré par diag\_consistency.py.
* zz-manifests/manifest\_report.md — rapport lisible.
* zz-manifests/figure\_manifest.csv — index des figures.
* zz-manifests/add\_to\_manifest.py ; zz-manifests/migration\_map.json.
* zz-manifests/meta\_template.json — gabarit de métadonnées (source maître).
* zz-manifests/README\_manifest.md — documentation manifeste.
* zz-manifests/diag\_consistency.py — diagnostic (présence/format/empreintes).
* zz-manifests/chapters/chapter\_manifest\_{

## 8) Conventions & styles
* conventions.md : normes de nommage (FR), unités (SI), précision numérique, format CSV/DAT/JSON, styles de figures, seuils de QA, sémantique des colonnes, règles pour jalons et classes (primaire/ordre2), etc.
* Cohérence inter-chapitres : les paramètres transverses (p. ex. alpha, q

## 9) Environnements & dépendances
* Python ≥ 3.1

## 1

## 11) Licence / Contact
* Licence : à préciser (interne / publique) — voir fichier LICENSE.
* Contact scientifique : responsable MCGT.
* Contact technique : mainteneur des scripts / CI.









