import re
import unittest

from jinja2 import Environment, FileSystemLoader, PrefixLoader


class ButtonMacroTests(unittest.TestCase):
    def _render(self, params):
        env = Environment(
            loader=PrefixLoader(
                {"jinja_ui_kit": FileSystemLoader("src/jinja_ui_kit/templates")}
            ),
            autoescape=True,
        )
        template = env.from_string(
            """
            {% from "jinja_ui_kit/components/button/macro.html" import button %}
            {{ button(params) }}
            """
        )
        return template.render(params=params)

    def _classes(self, html, tag):
        """Return the class list, ignoring look-alike attributes such as `data-class`."""
        match = re.search(rf'<{tag}\b[^>]*?\sclass="([^"]*)"', html)
        self.assertIsNotNone(match)
        return match.group(1)

    def test_link_button_does_not_wrap(self):
        html = self._render({"text": "Save and continue", "href": "/next"})

        self.assertIn("whitespace-nowrap", self._classes(html, "a"))

    def test_default_button_does_not_wrap(self):
        html = self._render({"text": "Save and continue"})

        self.assertIn("whitespace-nowrap", self._classes(html, "button"))

    def test_input_button_does_not_wrap(self):
        html = self._render({"name": "action", "value": "Save and continue"})

        self.assertIn("whitespace-nowrap", self._classes(html, "input"))

    def test_start_button_does_not_wrap(self):
        html = self._render({"text": "Start now", "href": "/start", "isStart": True})

        self.assertIn("whitespace-nowrap", self._classes(html, "a"))

    def test_prevent_double_click_marks_control_without_hyperscript(self):
        for params in (
            {"text": "Save"},
            {"name": "action", "value": "Save"},
            {"text": "Save", "href": "/next"},
        ):
            with self.subTest(params=params):
                html = self._render(dict(params, preventDoubleClick=True))

                self.assertIn('data-prevent-double-click="true"', html)
                self.assertNotIn('_="', html)

    def test_no_guard_by_default(self):
        html = self._render({"text": "Save and continue"})

        self.assertNotIn("data-prevent-double-click", html)

    def test_prevent_double_click_passes_caller_hyperscript_through(self):
        html = self._render(
            {
                "text": "Save and continue",
                "preventDoubleClick": True,
                "attributes": {"_": "on click log 1"},
            }
        )

        self.assertIn('_="on click log 1"', html)
        self.assertIn('data-prevent-double-click="true"', html)

    def test_prevent_double_click_keeps_prerendered_string_attributes(self):
        html = self._render(
            {
                "text": "Save and continue",
                "preventDoubleClick": True,
                "attributes": 'data-testid="save-button"',
            }
        )

        self.assertIn('data-testid="save-button"', html)
        self.assertIn('data-prevent-double-click="true"', html)


if __name__ == "__main__":
    unittest.main()
