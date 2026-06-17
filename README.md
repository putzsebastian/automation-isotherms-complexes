# Automated Isotherm Determination for Copper Catalysts

[![DOI](https://zenodo.org/badge/1252191941.svg)](https://doi.org/10.5281/zenodo.20427098)

Experiment template and instance scripts supporting the publication:

> **When Immobilization is not Covalent: Stable, Reusable Copper-Bispidine Catalysts on Agarose with Diffusion-Limited Turnover**
> 
> Nadjana Schneider, Sebastian Putz, Sebastian Fleer, Stefan Heißler, Eric Gottwald, Jonas Braun,  André Tschöpe, and Katharina Bleher


## Overview

This repository contains the automated workflow used to determine adsorption isotherms for copper catalysts on the BioCAR self-driving laboratory (SDL) platform. It is published to document and support the results reported in the paper above.

It contains three kinds of artifacts:

- **Experiment template** (`template/`) — the reusable workflow definition for an automated isotherm-determination campaign on the BioCAR SDL with parameter placeholders
- **Experiment instance scripts** (`experiment/`) — the concrete scripts, with parameters as actually executed, that produced the data reported in the paper
- **Raw CLSM data** (`data/`) — the raw confocal laser scanning microscopy image files (see [Data](#data))


## Repository structure

```
.
├── template/         # Reusable experiment template
├── experiment/       # Per-experiment instance scripts (as run for the paper)
├── data/             # Raw confocal laser scanning microscopy (CLSM) data
│   └── CLSM/         # CLSM acquisitions (Leica .lif)
├── LICENSE
└── README.md
```


## Data

The `data/` folder holds the raw confocal laser scanning microscopy (CLSM)
data. Acquisitions are stored under `data/CLSM/` as Leica Image Files (`.lif`),
each bundling the series recorded in one session and named by acquisition date
(`YYYYMMDD.lif`).

### `20260603.lif` — blank measurements

- **Series 1** — pure agarose beads
- **Series 2** — agarose beads with Lucifer Yellow (5 µM)

### `20260521.lif` — immobilized samples

- **Series 13** — preloaded agarose beads with [(L3)Cu<sup>II</sup>(MeCN)](OTf)₂
  (q<sub>m</sub> = 136.7 mg/g, q = 39.6 %) and Lucifer Yellow (5 µM)
- **Series 14** — preloaded agarose beads with Cu<sup>II</sup>(OTf)₂
  (q<sub>m</sub> = 158.3 mg/g, q = 99.6 %) and Lucifer Yellow (5 µM)

Fluorescence intensity profiles across the bead cross-section were obtained from
the image stacks of:

- **Series 10** — preloaded agarose beads with Cu<sup>II</sup>(OTf)₂
  (q<sub>m</sub> = 158.3 mg/g, q = 99.6 %) and Lucifer Yellow (5 µM)
- **Series 12** — preloaded agarose beads with [(L3)Cu<sup>II</sup>(MeCN)](OTf)₂
  (q<sub>m</sub> = 136.7 mg/g, q = 39.6 %) and Lucifer Yellow (5 µM)

`.lif` files can be opened with Leica LAS X or with open tools such as
[Bio-Formats](https://www.openmicroscopy.org/bio-formats/) / Fiji (ImageJ).


## Scope and reproducibility note

The scripts depend on the broader BioCAR SDL platform (hard- and software) and are provided as a record of what was executed plus the reusable template logic, rather than as a turnkey end-to-end pipeline.


## License

Released under the MIT License — see [`LICENSE`](LICENSE).

