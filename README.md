# Bat Actions Auto-Label Tool and SLEAP Model Evaluation

---

## Overview

This repository contains two main tools for working with bat action recognition datasets:

1. **Bat Actions Auto-Label Tool:** A GUI-based tool to help label actions of bats in videos, with support for auto-labeling using predefined Regions of Interest (ROI) and machine learning predictions.

Use as follow:

```bash

python /src/app.py 

```

2. **SLEAP Model Evaluation:** A Python script for evaluating SLEAP models using Object Keypoint Similarity (OKS) and localization error metrics, along with plotting utilities.

Use by:

```bash

python /src/evaluation.py 

```

with the relevant arguments

```bash
usage: evaluation.py [-h] --centroid_model_path CENTROID_MODEL_PATH
                     --centered_instance_model_path
                     CENTERED_INSTANCE_MODEL_PATH --project_path PROJECT_PATH

Evaluate two SLEAP models (centroid and centered instance) on a given project.

optional arguments:
  -h, --help            show this help message and exit
  --centroid_model_path CENTROID_MODEL_PATH
                        Path to the centroid SLEAP model.
  --centered_instance_model_path CENTERED_INSTANCE_MODEL_PATH
                        Path to the centered instance model.
  --project_path PROJECT_PATH
                        Path to the .slp file with ground truth labels.


```


---

## Requierments

- Python 3.x

- All **Sleap** platform dependencies. Use the platform installation (conda package manager is recommended).

- Tkinter (for GUI)

- shapley lib