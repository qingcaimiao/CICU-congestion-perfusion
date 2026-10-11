# Data access

## Source databases

| Database | Version | Access | Used for |
|---|---|---|---|
| MIMIC-IV | v3.1 | https://physionet.org/content/mimiciv/3.1/ | Development cohort |
| eICU Collaborative Research Database | v2.0 | https://physionet.org/content/eicu-crd/2.0/ | External replication |

Both require:

1. A PhysioNet account.
2. Completion of the CITI "Data or Specimens Only Research" training course.
3. A signed data use agreement (DUA).

## Why no data files are included

The DUAs for both databases **prohibit redistribution of patient-level data**. This repository therefore contains only:

* cohort-definition and analysis code, and
* aggregate outputs (counts, medians, odds ratios, confidence intervals, model metrics) that do not permit identification of any individual.

No file in `results/` contains a stay identifier, a subject identifier, a hospital identifier or any row-level record. Row-level prediction vectors and analysis datasets were deliberately excluded.

## Rebuilding the analysis

1. Obtain credentialed access to both databases.
2. Download MIMIC-IV v3.1 and eICU-CRD v2.0.
3. Point the path variables at the top of each script in the `code/` folder to your local installation.
4. Run the scripts in the order given in the README.

Runtime note: the MIMIC-IV build step scans `chartevents` (about 42 GB) and the eICU-CRD build step scans `nurseCharting` (about 11.5 GB). On a workstation with 8 threads this takes roughly 15-25 minutes per cohort.

## Timing of release

This repository accompanies a manuscript submitted for peer review. If the manuscript is accepted, the repository will be archived on Zenodo to obtain a citable DOI, and the DOI will be added to the manuscript's Data Availability Statement.
