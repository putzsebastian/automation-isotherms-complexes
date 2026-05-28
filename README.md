# Automated Isotherm Determination for Copper Catalysts

[![DOI](https://zenodo.org/badge/1252191941.svg)](https://doi.org/10.5281/zenodo.20427098)

Experiment template and instance scripts supporting the publication:

> **When Immobilization Isn’t Covalent: Stable, Non-Leaching Bispidine-Cu on Agarose with Diffusion-Limited Turnover**
> 
> Nadjana Schneider, Sebastian Putz, Sebastian Fleer, Stefan Heißler, Eric Gottwald, Jonas Braun,  André Tschöpe, and Katharina Bleher


## Overview

This repository contains the automated workflow used to determine adsorption isotherms for copper catalysts on the BioCAR self-driving laboratory (SDL) platform. It is published to document and support the results reported in the paper above.

It contains two kinds of artifact:

- **Experiment template** (`template/`) — the reusable workflow definition for an automated isotherm-determination campaign on the BioCAR SDL with parameter placeholders
- **Experiment instance scripts** (`experiment/`) — the concrete scripts, with parameters as actually executed, that produced the data reported in the paper


## Repository structure

```
.
├── template/         # Reusable experiment template(s)
├── experiment/       # Per-experiment instance scripts (as run for the paper)
├── LICENSE
└── README.md
```


## Scope and reproducibility note

The scripts depend on the broader BioCAR SDL platform (hard- and software) and are provided as a faithful recordof what was executed plus the reusable template logic, rather than as a turnkey end-to-end pipeline.


## License

Released under the MIT License — see [`LICENSE`](LICENSE).

