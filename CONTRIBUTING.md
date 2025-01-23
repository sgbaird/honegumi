```{todo} THIS IS SUPPOSED TO BE AN EXAMPLE. MODIFY IT ACCORDING TO YOUR NEEDS!

   The document assumes you are using a source repository service that promotes a
   contribution model similar to [GitHub's fork and pull request workflow].
   While this is true for the majority of services (like GitHub, GitLab,
   BitBucket), it might not be the case for private repositories (e.g., when
   using Gerrit).

   Also notice that the code examples might refer to GitHub URLs or the text
   might use GitHub specific terminology (e.g., *Pull Request* instead of *Merge
   Request*).

   Please make sure to check the document having these assumptions in mind
   and update things accordingly.
```

```{todo} Provide the correct links/replacements at the bottom of the document.
```

```{todo} You might want to have a look on [PyScaffold's contributor's guide],

   especially if your project is open source. The text should be very similar to
   this template, but there are a few extra contents that you might decide to
   also include, like mentioning labels of your issue tracker or automated
   releases.
```

# Contributing

Welcome to `honegumi` contributor's guide.

This document focuses on getting any potential contributor familiarized with
the development processes, but [other kinds of contributions] are also appreciated.

If you are new to using [git] or have never collaborated in a project previously,
please have a look at [contribution-guide.org]. Other resources are also
listed in the excellent [guide created by FreeCodeCamp] [^contrib1].

Please notice, all users and contributors are expected to be **open,
considerate, reasonable, and respectful**. When in doubt,
[Python Software Foundation's Code of Conduct] is a good reference in terms of
behavior guidelines.

## Issue Reports

If you experience bugs or general issues with `honegumi`, please have a look
on the [issue tracker].
If you don't see anything useful there, please feel free to fire an issue report.

:::{tip}
Please don't forget to include the closed issues in your search.
Sometimes a solution was already reported, and the problem is considered
**solved**.
:::

New issue reports should include information about your programming environment
(e.g., operating system, Python version) and steps to reproduce the problem.
Please try also to simplify the reproduction steps to a very minimal example
that still illustrates the problem you are facing. By removing other factors,
you help us to identify the root cause of the issue.

## Documentation Improvements

You can help improve `honegumi` docs by making them more readable and coherent, or
by adding missing information and correcting mistakes.

`honegumi` documentation uses [Sphinx] as its main documentation compiler.
This means that the docs are kept in the same repository as the project code, and
that any documentation update is done in the same way was a code contribution.

```{todo} Don't forget to mention which markup language you are using.

    e.g.,  [reStructuredText] or [CommonMark] with [MyST] extensions.
```
   :::{tip}
      Please notice that the [GitHub web interface] provides a quick way of
      propose changes in `honegumi`'s files. While this mechanism can
      be tricky for normal code contributions, it works perfectly fine for
      contributing to the docs, and can be quite handy.

      If you are interested in trying this method out, please navigate to
      the `docs` folder in the source [repository], find which file you
      would like to propose changes and click in the little pencil icon at the
      top, to open [GitHub's code editor]. Once you finish editing the file,
      please write a message in the form at the bottom of the page describing
      which changes have you made and what are the motivations behind them and
      submit your proposal.
   :::

When working on documentation changes in your local machine, you can
compile them using [tox] :

```
tox -e docs
```

and use Python's built-in web server for a preview in your web browser
(`http://localhost:8000`):

```
python3 -m http.server --directory 'docs/_build/html'
```

## Code Contributions

For a high-level roadmap of Honegumi's development, see https://github.com/sgbaird/honegumi/discussions/2. Honegumi uses Python, Javascript, Jinja2, pytest, and GitHub actions to automate the generation, testing, and deployment of templates with a focus on Bayesian optimization packages. As of 2023-08-21, only a single package ([Meta's Ax Platform](https://ax.dev) for a small set of features. However, the plumbing and logic that creates this is thorough and scalable. I focused first on getting all the pieces together before scaling up to many features (and thus slowing down the development cycle).

Here are some ways you can help with the project:
1. Use the tool and let us know what you think 😉
2. [Provide feedback](https://github.com/sgbaird/honegumi/discussions/2) on the overall organization, logic, and workflow of the project
3. Extend the Ax features to additional options (i.e., additional rows and options within rows) via direct edits to [ax/main.py.jinja](https://github.com/sgbaird/honegumi/blob/main/src/honegumi/ax/main.py.jinja)
4. Improve the `honegumi.html` and `honegumi.ipynb` templates (may also need to update `generate_scripts.py`). See below for more information.
5. Extend Honegumi to additional platforms such as BoFire or Atlas
6. Spread the word about the tool

For those unfamiliar with Jinja2, see the Google Colab tutorial: [_A Gentle Introduction to Jinja2_](https://colab.research.google.com/github/sgbaird/honegumi/blob/main/notebooks/1.0-sgb-gentle-introduction-jinja.ipynb). The main template file for Meta's Adaptive Experimentation (Ax) Platform is [`ax/main.py.jinja`](https://github.com/sgbaird/honegumi/blob/main/src/honegumi/ax/main.py.jinja). The main file that interacts with this template is at [`scripts/generate_scripts.py`](https://github.com/sgbaird/honegumi/blob/main/scripts/generate_scripts.py). The generated scripts are [available on GitHub](https://github.com/sgbaird/honegumi/tree/main/docs/generated_scripts/ax). Each script is tested [via `pytest`](https://github.com/sgbaird/honegumi/tree/main/tests) and [GitHub Actions](https://github.com/sgbaird/honegumi/actions/workflows/ci.yml) to ensure it can run error-free. Finally, the results are passed to [core/honegumi.html.jinja](https://github.com/sgbaird/honegumi/blob/main/src/honegumi/core/honegumi.html.jinja) and [core/honegumi.ipynb.jinja](https://github.com/sgbaird/honegumi/blob/main/src/honegumi/core/honegumi.ipynb.jinja) to create the scripts and notebooks, respectively.

NOTE: If you are committing some of the generated scripts or notebooks on Windows, you will [likely need to run this command](https://stackoverflow.com/questions/22575662/filename-too-long-in-git-for-windows) in a terminal (e.g., git bash) as an administrator to avoid an `lstat(...) Filename too long` error:

```bash
git config --system core.longpaths true
```

If working in GitHub Desktop, you will likely need to follow [these instructions](https://stackoverflow.com/a/74289583/13697228).

In its current form (as of 2024-06-04), Honegumi generates *many* files. This can become unwieldy when working with git, and you may find the command line interface of git to be less frustrating. For example, you can use the following to check for changes in the non-generated files.

```bash
git status -- :!docs/generated_scripts :!docs/generated_notebooks :!tests/generated_scripts
```

To only commit non-generated files, you can add all files and reset the generated ones.

```bash
git add .
git reset docs/generated_scripts docs/generated_notebooks tests/generated_scripts
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
│   └── core              <- Actual Python package where the main functionality goes.
├── tests                   <- Unit tests which can be run with `pytest`.
├── .coveragerc             <- Configuration for coverage reports of unit tests.
├── .isort.cfg              <- Configuration for git hook that sorts imports.
└── .pre-commit-config.yaml <- Configuration of pre-commit git hooks.
```

### Submit an issue

Before you work on any non-trivial code contribution it's best to first create
a report in the [issue tracker] to start a discussion on the subject.
This often provides additional considerations and avoids unnecessary work.

### Create an environment

Before you start coding, we recommend creating an isolated [virtual environment]
to avoid any problems with your installed Python packages.
This can easily be done via either [virtualenv]:

```
virtualenv <PATH TO VENV>
source <PATH TO VENV>/bin/activate
```

or [Miniconda]:

```
conda create -n honegumi python=3 six virtualenv pytest pytest-cov
conda activate honegumi
```

### Clone the repository

1. Create an user account on GitHub if you do not already have one.

2. Fork the project [repository]: click on the *Fork* button near the top of the
   page. This creates a copy of the code under your account on GitHub.

3. Clone this copy to your local disk:

   ```
   git clone git@github.com:YourLogin/honegumi.git
   cd honegumi
   ```

4. You should run:

   ```
   pip install -U pip setuptools -e .
   ```

   to be able to import the package under development in the Python REPL.

   ```{todo} if you are not using pre-commit, please remove the following item:
   ```

5. Install [pre-commit]:

   ```
   pip install pre-commit
   pre-commit install
   ```

   `honegumi` comes with a lot of hooks configured to automatically help the
   developer to check the code being written.

### Implement your changes

1. Create a branch to hold your changes:

   ```
   git checkout -b my-feature
   ```

   and start making changes. Never work on the main branch!

2. Start your work on this branch. Don't forget to add [docstrings] to new
   functions, modules and classes, especially if they are part of public APIs.

3. Add yourself to the list of contributors in `AUTHORS.rst`.

4. When you’re done editing, do:

   ```
   git add <MODIFIED FILES>
   git commit
   ```

   to record your changes in [git].

   ```{todo} if you are not using pre-commit, please remove the following item:
   ```

   Please make sure to see the validation messages from [pre-commit] and fix
   any eventual issues.
   This should automatically use [flake8]/[black] to check/fix the code style
   in a way that is compatible with the project.

   :::{important}
   Don't forget to add unit tests and documentation in case your
   contribution adds an additional feature and is not just a bugfix.

   Moreover, writing a [descriptive commit message] is highly recommended.
   In case of doubt, you can check the commit history with:

   ```
   git log --graph --decorate --pretty=oneline --abbrev-commit --all
   ```

   to look for recurring communication patterns.
   :::

5. Please check that your changes don't break any unit tests with:

   ```
   tox
   ```

   (after having installed [tox] with `pip install tox` or `pipx`).

   You can also use [tox] to run several other pre-configured tasks in the
   repository. Try `tox -av` to see a list of the available checks.

### Submit your contribution

1. If everything works fine, push your local branch to the remote server with:

   ```
   git push -u origin my-feature
   ```

2. Go to the web page of your fork and click "Create pull request"
   to send your changes for review.

   ```{todo} if you are using GitHub, you can uncomment the following paragraph

      Find more detailed information in [creating a PR]. You might also want to open
      the PR as a draft first and mark it as ready for review after the feedbacks
      from the continuous integration (CI) system or any required fixes.

   ```

### Troubleshooting

The following tips can be used when facing problems to build or test the
package:

1. Make sure to fetch all the tags from the upstream [repository].
   The command `git describe --abbrev=0 --tags` should return the version you
   are expecting. If you are trying to run CI scripts in a fork repository,
   make sure to push all the tags.
   You can also try to remove all the egg files or the complete egg folder, i.e.,
   `.eggs`, as well as the `*.egg-info` folders in the `src` folder or
   potentially in the root of your project.

2. Sometimes [tox] misses out when new dependencies are added, especially to
   `setup.cfg` and `docs/requirements.txt`. If you find any problems with
   missing dependencies when running a command with [tox], try to recreate the
   `tox` environment using the `-r` flag. For example, instead of:

   ```
   tox -e docs
   ```

   Try running:

   ```
   tox -r -e docs
   ```

3. Make sure to have a reliable [tox] installation that uses the correct
   Python version (e.g., 3.7+). When in doubt you can run:

   ```
   tox --version
   # OR
   which tox
   ```

   If you have trouble and are seeing weird errors upon running [tox], you can
   also try to create a dedicated [virtual environment] with a [tox] binary
   freshly installed. For example:

   ```
   virtualenv .venv
   source .venv/bin/activate
   .venv/bin/pip install tox
   .venv/bin/tox -e all
   ```

4. [Pytest can drop you] in an interactive session in the case an error occurs.
   In order to do that you need to pass a `--pdb` option (for example by
   running `tox -- -k <NAME OF THE FALLING TEST> --pdb`).
   You can also setup breakpoints manually instead of using the `--pdb` option.

## Maintainer tasks

### Releases

```{todo} This section assumes you are using PyPI to publicly release your package.

   If instead you are using a different/private package index, please update
   the instructions accordingly.
```

If you are part of the group of maintainers and have correct user permissions
on [PyPI], the following steps can be used to release a new version for
`honegumi`:

1. Make sure all unit tests are successful.
2. Tag the current commit on the main branch with a release tag, e.g., `v1.2.3`.
3. Push the new tag to the upstream [repository],
   e.g., `git push upstream v1.2.3`
4. Clean up the `dist` and `build` folders with `tox -e clean`
   (or `rm -rf dist build`)
   to avoid confusion with old builds and Sphinx docs.
5. Run `tox -e build` and check that the files in `dist` have
   the correct version (no `.dirty` or [git] hash) according to the [git] tag.
   Also check the sizes of the distributions, if they are too big (e.g., >
   500KB), unwanted clutter may have been accidentally included.
6. Run `tox -e publish -- --repository pypi` and check that everything was
   uploaded to [PyPI] correctly.

[^contrib1]: Even though, these resources focus on open source projects and
    communities, the general ideas behind collaborating with other developers
    to collectively create software are general and can be applied to all sorts
    of environments, including private companies and proprietary code bases.

### Dependency Management & Reproducibility

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

[black]: https://pypi.org/project/black/
[commonmark]: https://commonmark.org/
[contribution-guide.org]: http://www.contribution-guide.org/
[creating a pr]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request
[descriptive commit message]: https://chris.beams.io/posts/git-commit
[docstrings]: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
[first-contributions tutorial]: https://github.com/firstcontributions/first-contributions
[flake8]: https://flake8.pycqa.org/en/stable/
[git]: https://git-scm.com
[github web interface]: https://docs.github.com/en/github/managing-files-in-a-repository/managing-files-on-github/editing-files-in-your-repository
[github's code editor]: https://docs.github.com/en/github/managing-files-in-a-repository/managing-files-on-github/editing-files-in-your-repository
[github's fork and pull request workflow]: https://guides.github.com/activities/forking/
[guide created by freecodecamp]: https://github.com/freecodecamp/how-to-contribute-to-open-source
[miniconda]: https://docs.conda.io/en/latest/miniconda.html
[myst]: https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html
[other kinds of contributions]: https://opensource.guide/how-to-contribute
[pre-commit]: https://pre-commit.com/
[pypi]: https://pypi.org/
[pyscaffold's contributor's guide]: https://pyscaffold.org/en/stable/contributing.html
[pytest can drop you]: https://docs.pytest.org/en/stable/usage.html#dropping-to-pdb-python-debugger-at-the-start-of-a-test
[python software foundation's code of conduct]: https://www.python.org/psf/conduct/
[restructuredtext]: https://www.sphinx-doc.org/en/master/usage/restructuredtext/
[sphinx]: https://www.sphinx-doc.org/en/master/
[tox]: https://tox.readthedocs.io/en/stable/
[virtual environment]: https://realpython.com/python-virtual-environments-a-primer/
[virtualenv]: https://virtualenv.pypa.io/en/stable/


```{todo} Please review and change the following definitions:
```

[repository]: https://github.com/<USERNAME>/honegumi
[issue tracker]: https://github.com/<USERNAME>/honegumi/issues
