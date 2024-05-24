from os import path

OBJECTIVE_OPT_KEY = "objective"
MODEL_OPT_KEY = "model"
CUSTOM_GEN_KEY = "custom_gen"
EXISTING_DATA_KEY = "existing_data"
# USE_CONSTRAINTS_NAME = "use_constraint"
SUM_CONSTRAINT_KEY = "sum_constraint"
ORDER_CONSTRAINT_KEY = "order_constraint"
LINEAR_CONSTRAINT_KEY = "linear_constraint"
COMPOSITIONAL_CONSTRAINT_KEY = "composition_constraint"
CATEGORICAL_KEY = "categorical"
CUSTOM_THRESHOLD_KEY = "custom_threshold"
PREDEFINED_CANDIDATES_KEY = "predef_candidates"
FEATURIZATION_KEY = "featurize"
CONTEXTUAL_VAR_KEY = "context"
FIDELITY_OPT_KEY = "fidelity"
TASK_OPT_KEY = "task"
SYNCHRONY_OPT_KEY = "synchrony"  # single, batch, asynchronous
DUMMY_KEY = "dummy"
MODEL_KWARGS_KEY = "model_kwargs"

TEMPLATE_DIR = path.join("src", "honegumi", "ax")
CORE_TEMPLATE_DIR = path.join("src", "honegumi", "core")
GEN_SCRIPT_DIR = path.join("docs", "generated_scripts", "ax")
GEN_NOTEBOOK_DIR = path.join("docs", "generated_notebooks", "ax")
TEST_TEMPLATE_DIR = path.join("tests", "generated_scripts", "ax")
DOC_DIR = "docs"

RENDERED_KEY = "rendered_template"
IS_COMPATIBLE_KEY = "is_compatible"
PREAMBLE_KEY = "preamble"
