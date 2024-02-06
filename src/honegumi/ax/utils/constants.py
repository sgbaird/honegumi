from os import path

OBJECTIVE_OPT_NAME = "objective"
MODEL_OPT_NAME = "model"
CUSTOM_GEN_NAME = "custom_gen"
EXISTING_DATA_NAME = "existing_data"
# USE_CONSTRAINTS_NAME = "use_constraint"
SUM_CONSTRAINT_NAME = "sum_constraint"
ORDER_CONSTRAINT_NAME = "order_constraint"
LINEAR_CONSTRAINT_NAME = "linear_constraint"
COMPOSITIONAL_CONSTRAINT_NAME = "composition_constraint"
CATEGORICAL_NAME = "categorical"
USE_CUSTOM_THRESHOLD_NAME = "custom_threshold"
PREDEFINED_CANDIDATES_NAME = "predef_candidates"
FEATURIZATION_NAME = "featurize"
CONTEXTUAL_VAR_NAME = "context"
FIDELITY_OPT_NAME = "fidelity"
TASK_OPT_NAME = "task"
SYNCHRONY_OPT_NAME = "synchrony"  # single, batch, asynchronous

TEMPLATE_DIR = path.join("src", "honegumi", "ax")
CORE_TEMPLATE_DIR = path.join("src", "honegumi", "core")
GEN_SCRIPT_DIR = path.join("docs", "generated_scripts", "ax")
GEN_NOTEBOOK_DIR = path.join("docs", "generated_notebooks", "ax")
TEST_TEMPLATE_DIR = path.join("tests", "generated_scripts", "ax")
DOC_DIR = "docs"
MODEL_KWARGS_NAME = "model_kwargs"
