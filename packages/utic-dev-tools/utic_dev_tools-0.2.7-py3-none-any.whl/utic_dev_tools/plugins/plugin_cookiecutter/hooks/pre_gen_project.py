import re
import sys


def validate_no_spaces_or_special_chars(var_name, value):
    """Ensure the value contains only letters, numbers, or underscores."""
    if not re.match(r"^[a-z_]+$", value):
        print(
            f"❌ Error: '{var_name}' should only lowercase letters or underscores (no spaces or special characters)."
        )
        sys.exit(1)


validate_no_spaces_or_special_chars("type", "{{ cookiecutter.type }}")
validate_no_spaces_or_special_chars("subtype", "{{ cookiecutter.subtype }}")

print("✅ Creating plugin at plugin-{{ cookiecutter.type }}/{{ cookiecutter.subtype }}")
print("Next steps:")
print("  - cd plugin-{{ cookiecutter.type }}-{{ cookiecutter.subtype }}")
print("  - uv sync")
