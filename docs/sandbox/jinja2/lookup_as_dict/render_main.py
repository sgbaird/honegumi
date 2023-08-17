from os import path

from jinja2 import Environment, FileSystemLoader

# Define the path to your HTML template file
template_path = "main.html.jinja"
template_dir = "docs\\sandbox\\jinja2"

# Define your variables
option_rows = [
    {"name": "row1", "options": ["A", "B"]},
    {"name": "row2", "options": ["C", "D", "E"]},
    {"name": "row3", "options": ["F", "G"]},
]
lookup = {
    "A,C,F": "ACF",
    "A,C,G": "INVALID",
    "A,D,F": "ADF",
    "A,D,G": "ADG",
    "A,E,F": "AEF",
    "A,E,G": "AEG",
    "B,C,F": "BCF",
    "B,C,G": "BCG",
    "B,D,F": "INVALID",
    "B,D,G": "BDG",
    "B,E,F": "INVALID",
    "B,E,G": "BEG",
}

invalid_configs = [["B", "D", "F"], ["B", "E", "F"], ["A", "C", "G"]]

# Create a Jinja2 environment and load the template file
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template(template_path)

# Render the template with your variables
html = template.render(
    option_rows=option_rows, lookup=lookup, invalid_configs=invalid_configs
)

# Write the rendered HTML to a file
with open(path.join(template_dir, "main.html"), "w") as f:
    f.write(html)

1 + 1
