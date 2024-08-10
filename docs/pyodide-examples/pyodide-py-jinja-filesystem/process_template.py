from jinja2 import Template

# Define the Jinja2 template as a string (or fetch it similarly from the filesystem)
template_str = """
# This is a generated Python script
import random

# Generate a random number between {{ min_value }} and {{ max_value }}
random_number = random.randint({{ min_value }}, {{ max_value }})
print("Random number:", random_number)
"""

# Create a Jinja2 Template object
template = Template(template_str)

# Define the data to be rendered
data = {
    "min_value": 1,
    "max_value": 10,
}

# Render the template with the data
rendered_script = template.render(data)

# Execute the rendered script
exec(rendered_script)
