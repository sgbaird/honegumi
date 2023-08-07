# honegumi

```{note}
🚧 This package is still under construction. Contributions are welcome!
```

Honegumi (骨組み) is an interactive "skeleton code" generator for API tutorials focusing on optimization packages. For a high-level roadmap of Honegumi's development, see https://github.com/sgbaird/honegumi/discussions/2. The top-level interface will be something like the following:

```{raw} html
:file: sandbox/jinja2/main.html
```

For a list of generated scripts, see https://github.com/sgbaird/honegumi/tree/main/docs/generated_scripts/ax. As of 2023-08-07, the available options are limited. Each script is tested [via `pytest`](https://github.com/sgbaird/honegumi/tree/main/tests) and [GitHub Actions](https://github.com/sgbaird/honegumi/actions/workflows/ci.yml) to ensure it can run error-free.

## Contents

```{toctree}
:maxdepth: 2

Overview <readme>
Contributions & Help <contributing>
License <license>
Authors <authors>
Changelog <changelog>
Module Reference <api/modules>
GitHub Source <https://github.com/sparks-baird/xtal2png>
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`

[Sphinx]: http://www.sphinx-doc.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[reStructuredText]: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
[MyST]: https://myst-parser.readthedocs.io/en/latest/
