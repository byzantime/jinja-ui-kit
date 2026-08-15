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


if __name__ == "__main__":
    unittest.main()
