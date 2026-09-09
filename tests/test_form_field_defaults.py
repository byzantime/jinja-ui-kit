import re
import unittest

from jinja2 import Environment, FileSystemLoader, PrefixLoader


class FormFieldDefaultClassesTests(unittest.TestCase):
    def _env(self):
        return Environment(
            loader=PrefixLoader(
                {"jinja_ui_kit": FileSystemLoader("src/jinja_ui_kit/templates")}
            ),
            autoescape=True,
        )

    def _classes(self, html, tag):
        # Non-greedy up to the first whitespace-delimited `class`, so a custom
        # attribute such as `data-class` is not mistaken for the class list.
        match = re.search(rf'<{tag}\b[^>]*?\sclass="([^"]*)"', html)
        self.assertIsNotNone(match)
        return match.group(1)

    def _render_input(self, params):
        template = self._env().from_string(
            """
            {% from "jinja_ui_kit/components/input/macro.html" import input %}
            {{ input(params) }}
            """
        )
        return template.render(params=params)

    def _render_select(self, params):
        template = self._env().from_string(
            """
            {% from "jinja_ui_kit/components/select/macro.html" import select %}
            {{ select(params) }}
            """
        )
        return template.render(params=params)

    def _render_label(self, params):
        template = self._env().from_string(
            """
            {% from "jinja_ui_kit/components/label/macro.html" import label %}
            {{ label(params) }}
            """
        )
        return template.render(params=params)

    def _render_textarea(self, params):
        template = self._env().from_string(
            """
            {% from "jinja_ui_kit/components/textarea/macro.html" import textarea %}
            {{ textarea(params) }}
            """
        )
        return template.render(params=params)

    def test_input_ships_default_classes(self):
        html = self._render_input(
            {"name": "username", "label": {"text": "Username"}}
        )
        classes = self._classes(html, "input")

        self.assertIn("border-neutral-300", classes)
        self.assertIn("rounded-md", classes)

    def test_input_appends_custom_classes(self):
        html = self._render_input(
            {
                "name": "username",
                "label": {"text": "Username"},
                "classes": "custom-class",
            }
        )
        classes = self._classes(html, "input")

        self.assertIn("border-neutral-300", classes)
        self.assertIn("custom-class", classes)

    def test_input_error_uses_danger_classes_not_dead_class(self):
        html = self._render_input(
            {
                "name": "username",
                "label": {"text": "Username"},
                "errorMessage": {"text": "Required"},
            }
        )
        classes = self._classes(html, "input")

        self.assertIn("border-danger-500", classes)
        self.assertIn("focus:ring-danger-500", classes)
        self.assertNotIn("input--error", classes)

    def test_select_ships_default_classes(self):
        html = self._render_select({"name": "color", "items": []})
        classes = self._classes(html, "select")

        self.assertIn("border-neutral-300", classes)
        self.assertIn("rounded-md", classes)

    def test_select_appends_custom_classes(self):
        html = self._render_select(
            {"name": "color", "items": [], "classes": "custom-class"}
        )
        classes = self._classes(html, "select")

        self.assertIn("border-neutral-300", classes)
        self.assertIn("custom-class", classes)

    def test_label_ships_default_classes(self):
        html = self._render_label({"text": "Username", "for": "username"})
        classes = self._classes(html, "label")

        self.assertIn("text-neutral-700", classes)

    def test_label_appends_custom_classes(self):
        html = self._render_label(
            {"text": "Username", "for": "username", "classes": "custom-class"}
        )
        classes = self._classes(html, "label")

        self.assertIn("text-neutral-700", classes)
        self.assertIn("custom-class", classes)

    def test_textarea_still_ships_default_classes(self):
        html = self._render_textarea({"name": "bio", "label": {"text": "Bio"}})
        classes = self._classes(html, "textarea")

        self.assertIn("border-neutral-300", classes)


if __name__ == "__main__":
    unittest.main()
