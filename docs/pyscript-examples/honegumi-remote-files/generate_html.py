import json
from os import path

from jinja2 import Environment, FileSystemLoader

# Define the paths for the templates and output directory
template_dir = "docs/pyscript-examples/honegumi-remote-files/"
output_dir = "docs/pyscript-examples/honegumi-remote-files/"
template_name = "honegumi-pyscript.html.jinja"

# Set up the Jinja2 environment
env = Environment(loader=FileSystemLoader(template_dir))

# Load the Jinja2 template
template = env.get_template(template_name)

# Example data to be used for rendering
jinja_option_rows = [
    {"name": "row1", "options": ["A", "B"], "tooltip": "Tooltip for row1"},
    {"name": "row2", "options": ["C", "D", "E"], "tooltip": "Tooltip for row2"},
    {"name": "row3", "options": ["F", "G"], "tooltip": "Tooltip for row3"},
]

invalid_configs = [["B", "D", "F"], ["B", "E", "F"], ["A", "C", "G"]]

# Render the template with the context data
rendered_html = template.render(
    jinja_option_rows=jinja_option_rows, invalid_configs=json.dumps(invalid_configs)
)

# Write the rendered HTML to an output file
output_file = path.join(output_dir, "honegumi-pyscript.html")
with open(output_file, "w") as f:
    f.write(rendered_html)

print(f"HTML file rendered and saved to {output_file}")

1 + 1
