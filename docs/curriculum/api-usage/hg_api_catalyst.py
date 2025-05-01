from pprint import pprint

import honegumi
from honegumi.ax._ax import option_rows
from honegumi.ax.utils import constants as cst
from honegumi.core._honegumi import Honegumi

# Set up template paths
script_template_dir = honegumi.ax.__path__[0]
core_template_dir = honegumi.core.__path__[0]
script_template_name = "main.py.jinja"
core_template_name = "honegumi.html.jinja"

# Initialize Honegumi
hg = Honegumi(
    cst,
    option_rows,
    script_template_dir=script_template_dir,
    core_template_dir=core_template_dir,
    script_template_name=script_template_name,
    core_template_name=core_template_name,
)

# Configure for OER catalyst optimization
options_model = hg.OptionsModel(
    objective="multi",  # For multiple KPIs (efficiency, durability, cost)
    model="Default",  # Standard GP is suitable for this problem
    task="Single",  # Single task optimization
    categorical=True,  # For electrolyte type parameter
    sum_constraint=True,  # For metal fractions summing to 1
    order_constraint=False,  # No order constraints specified
    linear_constraint=False,  # No linear constraints beyond composition
    composition_constraint=True,  # Metal fractions must sum to 1
    custom_threshold=True,  # For minimum performance criteria
    existing_data=False,  # No historical data available
    synchrony="Single",  # Process one catalyst composition at a time
    visualize=True,  # Helpful for tracking optimization progress
)

# Print the configured options for review
print("Catalyst OER Optimization Configuration:")
pprint(options_model.model_dump())

# Generate the optimization script
result = hg.generate(options_model)

# Save to file
script_name = "oer_catalyst_optimization.py"
with open(script_name, "w") as f:
    f.write(result)

print(f"\nGenerated optimization script saved to {script_name}")
print("\nRun this script to execute the OER catalyst optimization")
