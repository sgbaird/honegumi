[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
<!-- These are examples of badges you might also want to add to your README. Update the URLs accordingly.
[![Built Status](https://api.cirrus-ci.com/github/<USER>/honegumi.svg?branch=main)](https://cirrus-ci.com/github/<USER>/honegumi)
[![ReadTheDocs](https://readthedocs.org/projects/honegumi/badge/?version=latest)](https://honegumi.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/honegumi/main.svg)](https://coveralls.io/r/<USER>/honegumi)
[![PyPI-Server](https://img.shields.io/pypi/v/honegumi.svg)](https://pypi.org/project/honegumi/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/honegumi.svg)](https://anaconda.org/conda-forge/honegumi)
[![Monthly Downloads](https://pepy.tech/badge/honegumi/month)](https://pepy.tech/project/honegumi)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/honegumi)
-->

![honegumi-logo](reports/figures/honegumi-logo.png)

> Honegumi (骨組み, pronounced "ho neh goo mee") is a work-in-progress package for
> interactively creating API tutorials with a focus on optimization packages such as Meta's Ax
> Platform. We are looking for contributors, so please let us know if you're interested!
> Start by taking a look at our "Gentle Introduction to Jinja2" notebook: <a href="https://colab.research.google.com/github/sgbaird/honegumi/blob/main/1.0-sgb-gentle-introduction-jinja.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

<!-- > Unlock the power of advanced optimization in materials science with Honegumi (骨組み,
> pronounced "ho-neh-goo-mee"), our interactive "skeleton code" generator. -->

<!-- TODO: refactor this paragraph to emphasize general API tutorial creation, and then focus in on materials science as one example that I'll be focusing on here -->

Real-world materials science optimization tasks are complex, involving noise, multiple fidelity levels, multiple objectives, many dimensions, constraints, and a mixture of numerical and categorical variables. However, the application of state-of-the-art algorithms to these materials science tasks has been limited. Meta's Adaptive Experimentation (Ax) platform is one of the few optimization platforms capable of handling these challenges without oversimplification. While Ax and its backbone, BoTorch, have gained traction in chemistry and materials science, advanced implementations are still challenging, even for veteran materials informatics practitioners. In addition to combining multiple algorithms, there are other logistical issues, such as using existing data, embedding physical descriptors, and modifying search spaces. To address these challenges, we present Honegumi (骨組み or "ho-neh-goo-mee"): An interactive "skeleton code" generator for materials-relevant optimization. Similar to [PyTorch's installation docs](https://pytorch.org/get-started/locally/), users interactively select advanced topics to generate robust templates that are unit-tested with invalid configurations crossed out. Honegumi is the first Bayesian optimization template generator of its kind, and we envision that this tool will reduce the barrier to entry for applying advanced Bayesian optimization to real-world materials science tasks.

NOTE: This repository is under active development. Let us know if you're interested in contributing!

## Installation

In order to set up the necessary environment:

1. review and uncomment what you need in `environment.yml` and create an environment `honegumi` with the help of [conda]:
   ```
   conda env create -f environment.yml
   ```
2. activate the new environment with:
   ```
   conda activate honegumi
   ```

> **_NOTE:_**  The conda environment will have honegumi installed in editable mode.
> Some changes, e.g. in `setup.cfg`, might require you to run `pip install -e .` again.


Optional and needed only once after `git clone`:

3. install several [pre-commit] git hooks with:
   ```bash
   pre-commit install
   # You might also want to run `pre-commit autoupdate`
   ```
   and checkout the configuration under `.pre-commit-config.yaml`.
   The `-n, --no-verify` flag of `git commit` can be used to deactivate pre-commit hooks temporarily.

4. install [nbstripout] git hooks to remove the output cells of committed notebooks with:
   ```bash
   nbstripout --install --attributes notebooks/.gitattributes
   ```
   This is useful to avoid large diffs due to plots in your notebooks.
   A simple `nbstripout --uninstall` will revert these changes.


Then take a look into the `scripts` and `notebooks` folders.

## Dependency Management & Reproducibility

1. Always keep your abstract (unpinned) dependencies updated in `environment.yml` and eventually
   in `setup.cfg` if you want to ship and install your package via `pip` later on.
2. Create concrete dependencies as `environment.lock.yml` for the exact reproduction of your
   environment with:
   ```bash
   conda env export -n honegumi -f environment.lock.yml
   ```
   For multi-OS development, consider using `--no-builds` during the export.
3. Update your current environment with respect to a new `environment.lock.yml` using:
   ```bash
   conda env update -f environment.lock.yml --prune
   ```
## Project Organization

```
├── AUTHORS.md              <- List of developers and maintainers.
├── CHANGELOG.md            <- Changelog to keep track of new features and fixes.
├── CONTRIBUTING.md         <- Guidelines for contributing to this project.
├── Dockerfile              <- Build a docker container with `docker build .`.
├── LICENSE.txt             <- License as chosen on the command-line.
├── README.md               <- The top-level README for developers.
├── configs                 <- Directory for configurations of model & application.
├── data
│   ├── external            <- Data from third party sources.
│   ├── interim             <- Intermediate data that has been transformed.
│   ├── processed           <- The final, canonical data sets for modeling.
│   └── raw                 <- The original, immutable data dump.
├── docs                    <- Directory for Sphinx documentation in rst or md.
├── environment.yml         <- The conda environment file for reproducibility.
├── models                  <- Trained and serialized models, model predictions,
│                              or model summaries.
├── notebooks               <- Jupyter notebooks. Naming convention is a number (for
│                              ordering), the creator's initials and a description,
│                              e.g. `1.0-fw-initial-data-exploration`.
├── pyproject.toml          <- Build configuration. Don't change! Use `pip install -e .`
│                              to install for development or to build `tox -e build`.
├── references              <- Data dictionaries, manuals, and all other materials.
├── reports                 <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures             <- Generated plots and figures for reports.
├── scripts                 <- Analysis and production scripts which import the
│                              actual PYTHON_PKG, e.g. train_model.
├── setup.cfg               <- Declarative configuration of your project.
├── setup.py                <- [DEPRECATED] Use `python setup.py develop` to install for
│                              development or `python setup.py bdist_wheel` to build.
├── src
│   └── sensei              <- Actual Python package where the main functionality goes.
├── tests                   <- Unit tests which can be run with `pytest`.
├── .coveragerc             <- Configuration for coverage reports of unit tests.
├── .isort.cfg              <- Configuration for git hook that sorts imports.
└── .pre-commit-config.yaml <- Configuration of pre-commit git hooks.
```

<!-- pyscaffold-notes -->

## Note

This project has been set up using [PyScaffold] 4.4.1 and the [dsproject extension] 0.7.2.

[conda]: https://docs.conda.io/
[pre-commit]: https://pre-commit.com/
[Jupyter]: https://jupyter.org/
[nbstripout]: https://github.com/kynan/nbstripout
[Google style]: http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[PyScaffold]: https://pyscaffold.org/
[dsproject extension]: https://github.com/pyscaffold/pyscaffoldext-dsproject
