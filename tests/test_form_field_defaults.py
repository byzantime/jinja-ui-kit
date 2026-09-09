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

    def _render(self, component, params):
        template = self._env().from_string(
            f"""
            {{% from "jinja_ui_kit/components/{component}/macro.html" import {component} %}}
            {{{{ {component}(params) }}}}
            """
        )
        return template.render(params=params)

    def test_input_ships_default_classes(self):
        html = self._render(
            "input", {"name": "username", "label": {"text": "Username"}}
        )
        classes = self._classes(html, "input")

        self.assertIn("border-neutral-300", classes)
        self.assertIn("rounded-md", classes)

    def test_input_appends_custom_classes(self):
        html = self._render(
            "input",
            {
                "name": "username",
                "label": {"text": "Username"},
                "classes": "custom-class",
            },
        )
        classes = self._classes(html, "input")

        self.assertIn("border-neutral-300", classes)
        self.assertIn("custom-class", classes)

    def test_input_error_uses_danger_classes_not_dead_class(self):
        html = self._render(
            "input",
            {
                "name": "username",
                "label": {"text": "Username"},
                "errorMessage": {"text": "Required"},
            },
        )
        classes = self._classes(html, "input")

        self.assertIn("border-danger-500", classes)
        self.assertIn("focus:ring-danger-500", classes)
        self.assertNotIn("input--error", classes)
        # border-neutral-300 must not coexist with border-danger-500: Tailwind
        # resolves same-specificity utility clashes by generated-stylesheet
        # order, not class-attribute order, so both present would silently
        # pick whichever the build happens to emit last, hiding the error
        # border regardless of html ordering.
        self.assertNotIn("border-neutral-300", classes)

    def test_select_ships_default_classes(self):
        html = self._render("select", {"name": "color", "items": []})
        classes = self._classes(html, "select")

        self.assertIn("border-neutral-300", classes)
        self.assertIn("rounded-md", classes)

    def test_select_ships_bg_white_background(self):
        html = self._render("select", {"name": "color", "items": []})
        classes = self._classes(html, "select")

        self.assertIn("bg-white", classes)
        self.assertNotIn("bg-neutral-100", classes)

    def test_select_appends_custom_classes(self):
        html = self._render(
            "select", {"name": "color", "items": [], "classes": "custom-class"}
        )
        classes = self._classes(html, "select")

        self.assertIn("border-neutral-300", classes)
        self.assertIn("custom-class", classes)

    def test_select_error_does_not_mix_neutral_and_danger_border(self):
        html = self._render(
            "select",
            {
                "name": "color",
                "items": [],
                "errorMessage": {"text": "Required"},
            },
        )
        classes = self._classes(html, "select")

        self.assertIn("border-danger-500", classes)
        self.assertIn("focus:border-danger-500", classes)
        self.assertNotIn("border-neutral-300", classes)
        self.assertNotIn("focus:border-transparent", classes)

    def test_label_ships_default_classes(self):
        html = self._render("label", {"text": "Username", "for": "username"})
        classes = self._classes(html, "label")

        self.assertIn("text-neutral-700", classes)

    def test_label_appends_custom_classes(self):
        html = self._render(
            "label",
            {"text": "Username", "for": "username", "classes": "custom-class"},
        )
        classes = self._classes(html, "label")

        self.assertIn("text-neutral-700", classes)
        self.assertIn("custom-class", classes)

    def test_textarea_still_ships_default_classes(self):
        html = self._render("textarea", {"name": "bio", "label": {"text": "Bio"}})
        classes = self._classes(html, "textarea")

        self.assertIn("border-neutral-300", classes)


if __name__ == "__main__":
    unittest.main()
