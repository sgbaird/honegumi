![honegumi-logo](https://github.com/sgbaird/honegumi/raw/main/reports/figures/honegumi-logo.png)

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
<br>

<!-- data-color-scheme="no-preference: light; light: light; dark: dark;"  -->

<!-- <iframe width="560" height="315" src="https://www.youtube.com/embed/IVaWl2tL06c?si=cFZxU3R2W9jOycLb" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe> -->

> Honegumi ("ho-nay-goo-mee"), which means "skeletal framework" in Japanese, is a package for interactively creating minimal working examples for advanced Bayesian optimization topics.

```{tip}
If you're new to Bayesian optimization, watch [A Gentle Introduction to Bayesian Optimization](https://youtu.be/IVaWl2tL06c?si=BsT8duYZ1i8Sa38B)
```

Real-world chemistry and materials science optimization tasks are complex! Here are some example features of these kinds of tasks:

| Topic           | Description |
| --------------- | ----------- |
| Noise           | Repeat measurements are stochastic |
| Multi-fidelity  | Some measurements are higher quality but much more costly |
| Multi-objective | Almost always, tasks have multiple properties that are important |
| High-dimensional| Like finding the proverbial "needle-in-a-haystack", the search spaces are enormous |
| Constraints     | Not all combinations of parameters are valid (i.e., constraints) |
| Mixed-variable  | Often there is a mixture of numerical and categorical variables |

<!-- Maybe alloy discovery slide as a figure? -->

However, applications of state-of-the-art algorithms to these materials science tasks have been limited. Advanced implementations are still challenging, even for veteran materials informatics practitioners. In addition to combining multiple algorithms, there are other logistical issues, such as using existing data, embedding physical descriptors, and modifying search spaces. To address these challenges, we present *Honegumi*, an interactive script generator for materials-relevant Bayesian optimization using the [Ax Platform](https://ax.dev/).

```{note}
Honegumi ([骨組み](https://translate.google.com/?sl=ja&tl=en&text=%E9%AA%A8%E7%B5%84%E3%81%BF&op=translate)), a Japanese word meaning *skeletal framework*, is technically pronounced "ho-nay-goo-mee", but you can also refer to this tool as "honey gummy" to make it easy to remember 😉
```

<!-- *Honegumi* is an interactive script generator for materials-relevant Bayesian optimization using the [Ax Platform](https://ax.dev/).  -->

Similar to [PyTorch's installation docs](https://pytorch.org/get-started/locally/), users interactively toggle the options to generate the desired code output. These scripts are unit-tested, and invalid configurations are crossed out. This means you can expect the scripts to run without throwing errors. Honegumi is *not* a wrapper for optimization packages; instead, think of it as an interactive tutorial generator. Honegumi is the first Bayesian optimization template generator of its kind, and we envision that this tool will reduce the barrier to entry for applying advanced Bayesian optimization to real-world materials science tasks. It also [pairs well with LLMs](#a-perfect-pairing-with-llms)!

<!-- Meta's [Adaptive Experimentation (Ax) platform](https://ax.dev/) is one of the few optimization platforms capable of handling these challenges without oversimplification. While Ax and its backbone, [BoTorch](https://botorch.org/), have gained traction in chemistry and materials science,  -->

<!-- Honegumi ([骨組み](https://translate.google.com/?sl=ja&tl=en&text=%E9%AA%A8%E7%B5%84%E3%81%BF&op=translate)), which means _skeletal framework_ in Japanese, is a package for interactively creating API tutorials with a focus on optimization packages such as Meta's Ax Platform.  -->

<!-- https://myst-parser.readthedocs.io/en/latest/syntax/images_and_figures.html -->

Interact with Honegumi using the grid below. Select one option per row and watch the template dynamically appear. Click the corresponding ![colab](https://colab.research.google.com/assets/colab-badge.svg) badge to open a self-contained Google Colab notebook for the selected script. Click the corresponding ![github](https://img.shields.io/badge/Open%20in%20GitHub-blue?logo=github&labelColor=grey) badge to view the script source code directly. For example, if you want a script that optimizes multiple objectives simultaneously (multi-objective) as a function of many parameters (high-dimensional), you would select `multi` from the `objective` option row and `FULLYBAYESIAN` from the `model` row. Hover your mouse over the 🛈 icon to the right of each row to learn more about each option.

```{raw} html
:file: honegumi.html
```

#

```{note} If you like this tool, please consider [starring it on GitHub](https://github.com/sgbaird/honegumi). If you're interested in contributing, reach out to [sterling.baird@utoronto.ca](mailto:sterling.baird@utoronto.ca) 😊
```

## A Perfect Pairing with LLMs

```{tip}
Use Honegumi with ChatGPT to create non-halucinatory, custom Bayesian optimization scripts. See an [example ChatGPT transcript](https://chat.openai.com/share/f1169938-f891-4060-8034-b137e82cd5af) and the two-minute video below.
```

LLMs are good at recognizing patterns but really bad at suggesting Bayesian optimization scripts from scratch. Since Honegumi is really good at programatically giving valid Bayes opt scripts, you can use Honegumi to get a template and then ask an LLM to adapt it to your use case. The two-minute video below shows how a Honegumi template can be adapted using an LLM (in our case, ChatGPT Plus) to a cookie taste optimization as a function of flour, sugar, and butter content.

<iframe width="560" height="315" src="https://www.youtube.com/embed/rnI2BvGgP9o?si=HGODRbP19MlkC662" title="YouTube video player" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## Contents

```{toctree}
:maxdepth: 2

🔰 Tutorials <tutorials>
📖 Concepts <concepts>
🧑‍💻 Development <development>
🌐 GitHub Source <https://github.com/sgbaird/honegumi>
```

<!-- Overview <readme> -->

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`

[Sphinx]: http://www.sphinx-doc.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[reStructuredText]: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
[MyST]: https://myst-parser.readthedocs.io/en/latest/

<script async defer src="https://buttons.github.io/buttons.js"></script>
