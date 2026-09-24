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
        # Non-greedy up to the first whitespace-delimited `class`, so a custom
        # attribute such as `data-class` is not mistaken for the class list.
        match = re.search(rf'<{tag}\b[^>]*?\sclass="([^"]*)"', html)
        self.assertIsNotNone(match)
        return match.group(1)

    def _hyperscript(self, html):
        match = re.search(r'_="([^"]*)"', html)
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

    def test_prevent_double_click_adds_hyperscript_guard(self):
        html = self._render({"text": "Save and continue", "preventDoubleClick": True})

        script = self._hyperscript(html)
        self.assertIn("is-submitting", script)
        self.assertIn("htmx:after:request", script)
        self.assertIn('data-prevent-double-click="true"', html)

    def test_prevent_double_click_adds_hyperscript_guard_on_input(self):
        html = self._render(
            {"name": "action", "value": "Save and continue", "preventDoubleClick": True}
        )

        script = self._hyperscript(html)
        self.assertIn("is-submitting", script)
        self.assertIn("htmx:after:request", script)
        self.assertIn('data-prevent-double-click="true"', html)

    def test_no_hyperscript_guard_by_default(self):
        html = self._render({"text": "Save and continue"})

        self.assertNotIn('_="', html)
        self.assertNotIn("data-prevent-double-click", html)

    def test_prevent_double_click_merges_caller_hyperscript(self):
        html = self._render(
            {
                "text": "Save and continue",
                "preventDoubleClick": True,
                "attributes": {"_": "on click log 1"},
            }
        )

        script = self._hyperscript(html)
        self.assertTrue(script.startswith("on click log 1"))
        self.assertIn("is-submitting", script)
        self.assertIn("htmx:after:request", script)

    def test_prevent_double_click_ignored_for_link_buttons(self):
        html = self._render(
            {"text": "Save and continue", "href": "/next", "preventDoubleClick": True}
        )

        self.assertNotIn('_="', html)
        self.assertIn('data-prevent-double-click="true"', html)

    def test_prevent_double_click_preserves_other_caller_attributes(self):
        html = self._render(
            {
                "text": "Save and continue",
                "preventDoubleClick": True,
                "attributes": {"data-testid": "save-button"},
            }
        )

        script = self._hyperscript(html)
        self.assertIn("is-submitting", script)
        self.assertIn('data-testid="save-button"', html)

    def test_prevent_double_click_skipped_for_prerendered_string_attributes(self):
        html = self._render(
            {
                "text": "Save and continue",
                "preventDoubleClick": True,
                "attributes": 'data-testid="save-button"',
            }
        )

        self.assertNotIn('_="', html)
        self.assertIn('data-testid="save-button"', html)
        self.assertIn('data-prevent-double-click="true"', html)


if __name__ == "__main__":
    unittest.main()
