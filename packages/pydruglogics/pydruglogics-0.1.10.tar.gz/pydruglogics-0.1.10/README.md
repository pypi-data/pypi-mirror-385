# PyDrugLogics

![PyDrugLogics Logo](https://raw.githubusercontent.com/druglogics/pydruglogics/main/logo.png)

[![DOI](https://joss.theoj.org/papers/10.21105/joss.08038/status.svg)](https://doi.org/10.21105/joss.08038)
[![PyPI version](https://img.shields.io/pypi/v/pydruglogics)](https://badge.fury.io/py/pydruglogics)
[![Test Status](https://github.com/druglogics/pydruglogics/actions/workflows/run-tests.yml/badge.svg)](https://github.com/druglogics/pydruglogics/actions/workflows/run-tests.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/druglogics/pydruglogics/blob/main/LICENSE)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://druglogics.github.io/pydruglogics/)


## Overview

PyDrugLogics is a Python package designed for constructing, optimizing Boolean Models and performs in-silico perturbations of the models.
### Core Features
- Construct Boolean model from `.sif` file
- Load Boolean model from `.bnet` file
- Optimize Boolean model
- Generate perturbed models
- Evaluate drug synergies

## Installation

**PyDrugLogics** can be installed via **PyPi**, **Conda**, or **directly from the source**.
### Install PyDrugLogics from PyPI

The process involves two steps to install the PyDrugLogics core package and its necessary external dependencies.

#### 1. Install PyDrugLogics via pip

```bash
pip install pydruglogics
```
#### 2. Install External Dependency

```bash
pip install -r https://raw.githubusercontent.com/druglogics/pydruglogics/main/requirements.txt
```
This will install the PyDrugLogics package and handle all dependencies automatically.


### Install PyDrugLogics via conda

```bash
conda install szlaura::pydruglogics
```

### Install from Source

For the latest development version, you can clone the repository and install directly from the source:

```bash
git clone https://github.com/druglogics/pydruglogics.git
cd pydruglogics
pip install .
pip install -r requirements.txt
```

## CoLoMoTo Notebook environment
PyDrugLogics is available in the CoLoMoTo Docker and Notebook starting from version `2025-01-01`.

### Setup CoLoMoTo Docker and Notebook

1. Install the helper script in a terminal:

```bash
    pip install -U colomoto-docker
```
2. Start the CoLoMoTo Notebook (a specific tag can also be given):


```bash
    colomoto-docker    # or colomoto-docker -V 2025-01-01
```

3. Open the Jupiter Notebook and navigate to the `tutorials` folder to find the `PyDrugLogics` folder hosting the pydruglogics tutorial notebook.


See more about the CoLoMoTo Docker and Notebook in the [documentation](https://colomoto.github.io/colomoto-docker/README.html).<br/>

## Testing
1. To run all tests and check code coverage, you need to install test dependencies:
```bash
    pip install -r requirements.txt
    pip install -e .[test]
```

2. Then, from the repository root, run:

```bash
    pytest tests
```

You should see a coverage report at the end.

## Documentation

For full **PyDrugLogics** documentation, visit the [GitHub Documentation](https://druglogics.github.io/pydruglogics/).

## Quick Start Guide

Here's a simple example to get you started:

```python
from pydruglogics.model.BooleanModel import BooleanModel
from pydruglogics.input.TrainingData import TrainingData
from pydruglogics.input.Perturbations import Perturbation
from pydruglogics.input.ModelOutputs import ModelOutputs
from pydruglogics.execution.Executor import execute

# Initialize train and predict
model_outputs_dict = {
        "RSK_f": 1.0,
        "MYC": 1.0,
        "TCF7_f": 1.0
    }
model_outputs = ModelOutputs(input_dictionary=model_outputs_dict)

observations = [(["CASP3:0", "CASP8:0","CASP9:0","FOXO_f:0","RSK_f:1","CCND1:1"], 1.0)]
training_data = TrainingData(observations=observations)


drug_data = [['PI', 'PIK3CA', 'inhibits'],
            ['PD', 'MEK_f', 'activates'],
            ['CT','GSK3_f']]
perturbations = Perturbation(drug_data=drug_data)


boolean_model = BooleanModel(file='./ags_cascade_1.0/network.bnet', model_name='test', mutation_type='topology',
                                  attractor_tool='mpbn', attractor_type='trapspaces')

observed_synergy_scores = ["PI-PD", "PI-5Z", "PD-AK", "AK-5Z"]


ga_args = {
        'num_generations': 20,
        'num_parents_mating': 3,
        'mutation_num_genes': 3,
        'fitness_batch_size': 20
}

ev_args = {
        'num_best_solutions': 3,
        'num_of_runs': 30,
        'num_of_cores': 4
}


train_params = {
        'boolean_model': boolean_model,
        'model_outputs': model_outputs,
        'training_data': training_data,
        'ga_args': ga_args,
        'ev_args': ev_args
}

predict_params = {
        'perturbations': perturbations,
        'model_outputs': model_outputs,
        'observed_synergy_scores': observed_synergy_scores,
        'synergy_method': 'bliss'
}

# run train and predict
execute(train_params=train_params, predict_params=predict_params)
```

For a more detailed tutorial, please visit the [documentation](https://druglogics.github.io/pydruglogics/) or the [tutorial](https://github.com/druglogics/pydruglogics/blob/2400a153f15a884222f6fdabe705df1a5981ef54/tutorials/pydruglogics_tutorial.ipynb).

## Contributing to PyDrugLogics

We welcome contributions to **PyDrugLogics**!  

### How to Contribute

1. **Fork and clone** the repository:
   ```bash
   git clone https://github.com/druglogics/pydruglogics.git
   cd pydruglogics
   ```
2. **Create a feature branch**:
   ```bash
   git checkout -b my-feature-branch
   ```
3. **Make changes** and **write tests** for new features or bug fixes.
4. **Run tests** to ensure everything works:
   ```bash
   pytest tests
   ```
5. **Commit and push** your changes:
   ```bash
   git commit -m "Describe your changes"
   git push origin my-feature-branch
   ```
6. **Open a pull request** against the main repository.

### Guidelines

- Follow **PEP8** code style.  
- Write **clear commit messages**.  
- Update documentation if adding new functionality.  
- Ensure all tests pass before submitting a PR.  
- For new features or significant changes, we recommend opening an issue or discussing with the maintainer 
[@szlaura](https://github.com/szlaura) first.

### Reporting Issues

If you encounter a bug or wish to request a feature, please report it on our GitHub issue tracker:  

[GitHub Issues Page](https://github.com/druglogics/pydruglogics/issues)

When reporting an issue, include:

- Your operating system and version (e.g., Ubuntu 22.04)  
- Python version (e.g., Python 3.11.10)  
- The error message and traceback (if applicable)  
- Steps to reproduce the issue  

Thank you for your help!

## Citing PyDrugLogics

If you use PyDrugLogics, please cite the paper:

*Szekeres, L., Zobolas, J. (2025): PyDrugLogics: A Python Package for Predicting Drug Synergies Using Boolean Models. [DOI: 10.21105/joss.08038](https://doi.org/10.21105/joss.08038)*

```bibtex
@article{Szekeres2025,
  doi = {10.21105/joss.08038},
  url = {https://doi.org/10.21105/joss.08038},
  year = {2025},
  publisher = {The Open Journal},
  volume = {10},
  number = {114},
  pages = {8038},
  author = {Szekeres, Laura and Zobolas, John},
  title = {PyDrugLogics: A Python Package for Predicting Drug Synergies Using Boolean Models},
  journal = {Journal of Open Source Software}
}
```
