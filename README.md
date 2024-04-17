[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![ReadTheDocs](https://readthedocs.org/projects/honegumi/badge/?version=latest)](https://honegumi.readthedocs.io/en/latest/)
[![tests](https://github.com/sgbaird/honegumi/actions/workflows/ci.yml/badge.svg)](https://github.com/sgbaird/honegumi/actions/workflows/ci.yml)
[![GitHub issues](https://img.shields.io/github/issues/sgbaird/honegumi)](https://github.com/sgbaird/honegumi/issues)
[![GitHub Discussions](https://img.shields.io/github/discussions/sgbaird/honegumi)](https://github.com/sgbaird/honegumi/discussions)
[![Last Committed](https://img.shields.io/github/last-commit/sgbaird/honegumi)](https://github.com/sgbaird/honegumi/commits/main/)

<!-- These are examples of badges you might also want to add to your README. Update the URLs accordingly.
[![Built Status](https://api.cirrus-ci.com/github/<USER>/honegumi.svg?branch=main)](https://cirrus-ci.com/github/<USER>/honegumi)
[![PyPI-Server](https://img.shields.io/pypi/v/honegumi.svg)](https://pypi.org/project/honegumi/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/honegumi/main.svg)](https://coveralls.io/r/<USER>/honegumi)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/honegumi.svg)](https://anaconda.org/conda-forge/honegumi)
[![Monthly Downloads](https://pepy.tech/badge/honegumi/month)](https://pepy.tech/project/honegumi)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/honegumi)
<a href="https://colab.research.google.com/github/sgbaird/honegumi/blob/main/notebooks/1.0-sgb-gentle-introduction-jinja.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
-->

![honegumi-logo](reports/figures/honegumi-logo.png)

> Honegumi (骨組み, pronounced "ho neh goo mee"), which means "skeletal framework" in Japanese, is a package for
> interactively creating API tutorials with a focus on optimization packages such as Meta's Ax
> Platform. We are [looking for contributors](https://github.com/sgbaird/honegumi/blob/main/CONTRIBUTING.md)!

<!-- > Unlock the power of advanced optimization in materials science with Honegumi (骨組み,
> pronounced "ho-neh-goo-mee"), our interactive "skeleton code" generator. -->

<!-- TODO: refactor this paragraph to emphasize general API tutorial creation, and then focus in on materials science as one example that I'll be focusing on here -->

# Honegumi

Real-world materials science optimization tasks are complex! To cite a few examples:

| Topic           | Description |
| --------------- | ----------- |
| Noise           | Repeat measurements are stochastic |
| Multi-fidelity  | Some measurements are higher quality but much more costly |
| Multi-objective | Almost always, tasks have multiple properties that are important |
| High-dimensional| Like finding the proverbial "needle-in-a-haystack", the search spaces are enormous |
| Constraints     | Not all combinations of parameters are valid (i.e., constraints) |
| Mixed-variable  | Often there is a mixture of numerical and categorical variables |

However, applications of state-of-the-art algorithms to these materials science tasks have been limited. Meta's Adaptive Experimentation (Ax) platform is one of the few optimization platforms capable of handling these challenges without oversimplification. While Ax and its backbone, BoTorch, have gained traction in chemistry and materials science, advanced implementations are still challenging, even for veteran materials informatics practitioners. In addition to combining multiple algorithms, there are other logistical issues, such as using existing data, embedding physical descriptors, and modifying search spaces. To address these challenges, we present Honegumi (骨組み or "ho-neh-goo-mee"): An interactive "skeleton code" generator for materials-relevant optimization. Similar to [PyTorch's installation docs](https://pytorch.org/get-started/locally/), users interactively select advanced topics to generate robust templates that are unit-tested with invalid configurations crossed out. Honegumi is the first Bayesian optimization template generator of its kind, and we envision that this tool will reduce the barrier to entry for applying advanced Bayesian optimization to real-world materials science tasks.

## Quick Start

You don't need to install anything. Just navigate to https://honegumi.readthedocs.io/, select the desired options, and click the "Open in Colab" badge.

If you're interested in collaborating, see [the contribution
guidelines](https://github.com/sgbaird/honegumi/blob/main/CONTRIBUTING.md) and [the high-level roadmap of Honegumi's development](https://github.com/sgbaird/honegumi/discussions/2).

## License

[![GitHub License](https://img.shields.io/github/license/sgbaird/honegumi)](https://github.com/sgbaird/honegumi/blob/main/LICENSE.txt)

## Note

This project has been set up using [PyScaffold] 4.4.1 and the [dsproject extension] 0.7.2.

[conda]: https://docs.conda.io/
[pre-commit]: https://pre-commit.com/
[Jupyter]: https://jupyter.org/
[nbstripout]: https://github.com/kynan/nbstripout
[Google style]: http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[PyScaffold]: https://pyscaffold.org/
[dsproject extension]: https://github.com/pyscaffold/pyscaffoldext-dsproject
