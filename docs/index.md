![honegumi-logo](https://github.com/sgbaird/honegumi/raw/main/reports/figures/honegumi-logo.png)

<div style="text-align: center;">
    <a class="github-button" href="https://github.com/sgbaird/honegumi"
    data-icon="octicon-star" data-size="large" data-show-count="true" aria-label="Star
    sgbaird/honegumi on GitHub">Star</a>
    <a class="github-button"
    href="https://github.com/sgbaird" data-size="large" data-show-count="true"
    aria-label="Follow @sgbaird on GitHub">Follow @sgbaird</a>
    <a class="github-button" href="https://github.com/sgbaird/honegumi/subscription" data-icon="octicon-eye" data-size="large" data-show-count="true" aria-label="Watch sgbaird/honegumi on GitHub">Watch</a>
    <a class="github-button" href="https://github.com/sgbaird/honegumi/issues"
    data-icon="octicon-issue-opened" data-size="large" data-show-count="true"
    aria-label="Issue sgbaird/honegumi on GitHub">Issue</a>
    <a class="github-button" href="https://github.com/sgbaird/honegumi/discussions" data-icon="octicon-comment-discussion" data-size="large" aria-label="Discuss sgbaird/honegumi on GitHub">Discuss</a>
</div>
<br>

<!-- data-color-scheme="no-preference: light; light: light; dark: dark;"  -->

<!-- <iframe width="560" height="315" src="https://www.youtube.com/embed/IVaWl2tL06c?si=cFZxU3R2W9jOycLb" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe> -->

<div style="text-align: center;">
    <em>Honegumi ('ho-nay-goo-mee'), which means "skeletal framework" in Japanese, is a package for interactively creating minimal working examples for advanced Bayesian optimization topics.</em>
</div>
<br>

# Honegumi: An Interface for Accelerating the Adoption of Bayesian Optimization in the Experimental Sciences [![arXiv](https://img.shields.io/badge/arXiv-2502.06815-red.svg)](https://arxiv.org/abs/2502.06815)

```{tip}
New to Bayesian optimization? Start with [A Gentle Introduction to Bayesian Optimization](https://youtu.be/IVaWl2tL06c) and explore our [concept guides](https://honegumi.readthedocs.io/en/latest/concepts.html) and [coding tutorials](https://honegumi.readthedocs.io/en/latest/tutorials.html) on key optimization principles.
```

Real-world chemistry and materials science optimization tasks are complex! Noise, objectives, tasks, parameters, parameter types, and constraints riddle our optimization campaigns. However, applying state-of-the-art algorithms to these tasks isn't trivial, even for veteran materials informatics practitioners. Additionally, python libraries can be cumbersome to learn and use serving as a barrier to entry for interested users. To address these challenges, we present Honegumi, an interactive script generator for materials-relevant Bayesian optimization using the [Ax Platform](https://ax.dev/).

**Create your optimization script using the grid below!**
 Select options from each row to generate a code template. Hover over the **&#9432;** icons to get more information and see whether it’s a good choice.

```{raw} html
:file: honegumi.html
```

## What's the scope of honegumi?

Similar to [PyTorch's installation docs](https://pytorch.org/get-started/locally/), users interactively toggle the options to generate the desired code output. These scripts are unit-tested, and invalid configurations are crossed out. This means you can expect the scripts to run without throwing errors. Honegumi is *not* a wrapper for optimization packages; instead, think of it as an interactive tutorial generator. Honegumi is the first Bayesian optimization template generator of its kind, and we envision that this tool will reduce the barrier to entry for applying advanced Bayesian optimization to real-world science tasks.

```{note}
If you like this tool, please consider [starring it on GitHub](https://github.com/sgbaird/honegumi). If you're interested in contributing, reach out to [sterling.baird@utoronto.ca](mailto:sterling.baird@utoronto.ca) 😊
```

## Concept Docs and Tutorials

Understanding Bayesian optimization requires both theoretical knowledge and practical experience. Our documentation is structured to support this dual approach. The [concept guides](https://honegumi.readthedocs.io/en/latest/concepts.html) provide in-depth explanations of fundamental principles, from the basics of single-objective optimization to advanced topics like multitask optimization and fully Bayesian Gaussian process models. These theoretical foundations are complemented by hands-on [coding tutorials](https://honegumi.readthedocs.io/en/latest/tutorials.html) that demonstrate real-world applications across various materials science domains.

The tutorials walk you through practical scenarios such as optimizing 3D printed materials, developing biodegradable polymers with specific strength requirements, and efficiently screening anti-corrosion coatings. Each tutorial bridges theory and practice, showing how to apply advanced optimization concepts to solve tangible engineering challenges. Whether you're new to Bayesian optimization or looking to implement sophisticated multi-objective strategies, our documentation provides the guidance needed to successfully apply these techniques to your specific materials science challenges.

## A Perfect Pairing with LLMs

```{tip}
Use Honegumi with ChatGPT to create non-halucinatory, custom Bayesian optimization scripts. See an [example ChatGPT transcript](https://chat.openai.com/share/f1169938-f891-4060-8034-b137e82cd5af) and the videos below.
```

While Large Language Models excel at pattern recognition, they often struggle to create reliable Bayesian optimization scripts from scratch. Honegumi complements LLMs by providing validated templates that can then be customized through LLM assistance. Watch below as we demonstrate this workflow by optimizing a cookie recipe using Honegumi and ChatGPT:

### Basic demo: Cookie Optimization (no audio)

<iframe width="560" height="315" src="https://www.youtube.com/embed/rnI2BvGgP9o?si=HGODRbP19MlkC662" title="YouTube video player" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

### Overview

<iframe width="560" height="315" src="https://www.youtube.com/embed/1d1rlCyk85g?si=QF_Yn0I3RCddgMP9" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### Tutorial #2 walkthrough

<iframe width="560" height="315" src="https://www.youtube.com/embed/T5DWycXu1SY?si=dLl83jYQSntXOPqx" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Citing

If you find Honegumi useful, please consider citing:

> Baird, Sterling G., Andrew R. Falkowski, and Taylor D. Sparks. "Honegumi: An Interface for Accelerating the Adoption of Bayesian Optimization in the Experimental Sciences." *arXiv*, February 4, 2025. https://doi.org/10.48550/arXiv.2502.06815.

```bibtex
@misc{baird_honegumi_2025,
  title = {Honegumi: {{An Interface}} for {{Accelerating}} the {{Adoption}} of {{Bayesian Optimization}} in the {{Experimental Sciences}}},
  shorttitle = {Honegumi},
  author = {Baird, Sterling G. and Falkowski, Andrew R. and Sparks, Taylor D.},
  year = {2025},
  month = feb,
  number = {arXiv:2502.06815},
  eprint = {2502.06815},
  primaryclass = {cs},
  publisher = {arXiv},
  doi = {10.48550/arXiv.2502.06815},
  archiveprefix = {arXiv},
  keywords = {Computer Science - Machine Learning,Condensed Matter - Materials Science},
}
```

Zenodo snapshots of the GitHub releases (beginning with `v0.3.2`) are available at [![DOI](https://zenodo.org/badge/658136354.svg)](https://doi.org/10.5281/zenodo.14949415)

## Contents

```{toctree}
:maxdepth: 2

🔰 Tutorials <tutorials>
📖 Concepts <concepts>
🧑‍💻 Development <development>
🌐 GitHub Source <https://github.com/sgbaird/honegumi>
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`

[Sphinx]: http://www.sphinx-doc.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[reStructuredText]: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
[MyST]: https://myst-parser.readthedocs.io/en/latest/

<script async defer src="https://buttons.github.io/buttons.js"></script>
