"""Asset management utilities for jinja-ui-kit."""

from importlib.resources import files


def get_css_path() -> str:
    """Get the path to the jinja-ui-kit CSS file.

    Returns:
        str: Absolute path to the jinja-ui-kit.min.css file

    Raises:
        FileNotFoundError: If the CSS file is not found
    """
    css_file = files("jinja_ui_kit") / "dist" / "jinja-ui-kit.min.css"
    return str(css_file)
