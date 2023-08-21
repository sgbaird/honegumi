
# honegumi

```{note}
🚧 This package is under active development. We are looking for contributors, so please let us know if you're interested!
```

Honegumi ([骨組み](https://translate.google.com/?sl=ja&tl=en&text=%E9%AA%A8%E7%B5%84%E3%81%BF&op=translate)), which means "skeletal framework" in Japanese, is a work-in-progress package for interactively creating API tutorials with a focus on optimization packages such as Meta's Ax Platform. You can interact with Honegumi "in the flesh." In the interactive grid below, select one option per row and watch the template dynamically appear. Click the "Open in Colab" badge to open a self-contained Google Colab notebook corresponding to the selected template. Click "Open in GitHub" to view the notebook source directly.

```{raw} html
:file: honegumi.html
```

For a high-level roadmap of Honegumi's development, see https://github.com/sgbaird/honegumi/discussions/2. Start by looking at [our contribution guide](https://honegumi.readthedocs.io/en/latest/contributing.html) and our Google Colab tutorial: [_A Gentle Introduction to Jinja2_](https://colab.research.google.com/github/sgbaird/honegumi/blob/main/notebooks/1.0-sgb-gentle-introduction-jinja.ipynb). The generated scripts are [available on GitHub](https://github.com/sgbaird/honegumi/tree/main/docs/generated_scripts/ax). Each script is tested [via `pytest`](https://github.com/sgbaird/honegumi/tree/main/tests) and [GitHub Actions](https://github.com/sgbaird/honegumi/actions/workflows/ci.yml) to ensure it can run error-free. The main template file for Meta's Adaptive Experimentation (Ax) Platform is [`ax/main.py.jinja`](https://github.com/sgbaird/honegumi/blob/main/src/honegumi/ax/main.py.jinja). The main file that interacts with this template is at [`scripts/generate_scripts.py`](https://github.com/sgbaird/honegumi/blob/main/scripts/generate_scripts.py).

## Contents

```{toctree}
:maxdepth: 2

Overview <readme>
Contributions & Help <contributing>
License <license>
Authors <authors>
Changelog <changelog>
Module Reference <api/modules>
GitHub Source <https://github.com/sgbaird/honegumi>
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`

[Sphinx]: http://www.sphinx-doc.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[reStructuredText]: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
[MyST]: https://myst-parser.readthedocs.io/en/latest/
