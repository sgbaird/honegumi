from os import path

OBJECTIVE_OPT_NAME = "objective"
MODEL_OPT_NAME = "model"
USE_CUSTOM_GEN_OPT_NAME = "use_custom_gen"
USE_EXISTING_DATA_NAME = "use_existing_data"
USE_CONSTRAINTS_NAME = "use_constraint"
USE_CATEGORICAL_NAME = "use_categorical"
USE_CUSTOM_THRESHOLD_NAME = "use_custom_threshold"
TEMPLATE_DIR = path.join("src", "honegumi", "ax")
CORE_TEMPLATE_DIR = path.join("src", "honegumi", "core")
GEN_SCRIPT_DIR = path.join("docs", "generated_scripts", "ax")
GEN_NOTEBOOK_DIR = path.join("docs", "generated_notebooks", "ax")
TEST_TEMPLATE_DIR = path.join("tests", "generated_scripts", "ax")
DOC_DIR = "docs"
MODEL_KWARGS_NAME = "model_kwargs"
