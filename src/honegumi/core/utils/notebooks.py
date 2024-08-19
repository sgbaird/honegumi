import io
from os import path
from urllib.parse import quote, urljoin

import jupytext

import honegumi.ax.utils.constants as cst
import honegumi.core.utils.constants as core_cst


def create_notebook(datum, gen_script_path, script, cst=cst):
    github_username = "sgbaird"
    github_prefix = f"https://github.com/{github_username}/honegumi/tree/main/"
    github_link = urljoin(github_prefix, gen_script_path)

    github_badge = f'<a href="{github_link}"><img alt="Open in GitHub" src="https://img.shields.io/badge/Open%20in%20GitHub-blue?logo=github&labelColor=grey"></a>'  # noqa E501

    colab_prefix = (
        "https://colab.research.google.com/github/sgbaird/honegumi/blob/main/"
    )

    notebook_fname = f"{datum['stem']}.ipynb"
    notebook_path = path.join(cst.GEN_NOTEBOOK_DIR, notebook_fname)
    # HACK: issue with + encoding becoming %20 instead of %2B due to use of \\,
    # and maybe other issues (hence both quote fn and replace line)
    encoded_notebook_fname = quote(notebook_fname)
    encoded_notebook_path = path.join(cst.GEN_NOTEBOOK_DIR, encoded_notebook_fname)
    colab_link = urljoin(colab_prefix, encoded_notebook_path).replace("\\", "/")
    colab_badge = f'<a href="{colab_link}"><img alt="Open In Colab" src="https://colab.research.google.com/assets/colab-badge.svg"></a>'  # noqa E501

    preamble = f"{colab_badge} {github_badge}"
    datum[core_cst.PREAMBLE_KEY] = preamble  # for the HTML template

    # create an intermediate file object for gen_script and prepend colab link
    nb_text = f"# %% [markdown]\n{colab_badge}\n\n# %%\n%pip install ax-platform\n\n# %%\n{script}"  # noqa E501
    gen_script_file = io.StringIO(nb_text)

    # generate the notebook
    notebook = jupytext.read(gen_script_file, fmt="py:percent")

    with open(notebook_path, "w") as f:
        jupytext.write(notebook, f, fmt="notebook")

    return notebook, notebook_path
