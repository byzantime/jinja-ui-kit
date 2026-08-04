import re
import unittest

from jinja2 import Environment, FileSystemLoader, PrefixLoader


class ModalMacroTests(unittest.TestCase):
    def _render(self, params):
        env = Environment(
            loader=PrefixLoader(
                {"jinja_ui_kit": FileSystemLoader("src/jinja_ui_kit/templates")}
            ),
            autoescape=True,
        )
        template = env.from_string(
            """
            {% from "jinja_ui_kit/components/modal/macro.html" import modal %}
            {% call modal(params) %}<p>Modal body</p>{% endcall %}
            """
        )
        return template.render(params=params)

    def _style(self, html):
        match = re.search(r'<div[^>]*id="[^"]*-content"[^>]*style="([^"]*)"', html)
        self.assertIsNotNone(match)
        return match.group(1)

    def test_fullscreen_sets_fixed_height_and_max_height(self):
        html = self._render({"size": "fullscreen"})
        style = self._style(html)

        self.assertIn("max-height: 98vh", style)
        self.assertIn("height: 98vh", style)

    def test_fullscreen_respects_explicit_max_height(self):
        html = self._render({"size": "fullscreen", "maxHeight": "80vh"})
        style = self._style(html)

        self.assertIn("max-height: 80vh", style)
        self.assertIn("height: 98vh", style)

    def test_default_size_does_not_set_fixed_height(self):
        html = self._render({})
        style = self._style(html)

        self.assertIn("max-height: 90vh", style)
        self.assertNotIn("; height:", style)
        self.assertNotRegex(style, r"^height:")


if __name__ == "__main__":
    unittest.main()
