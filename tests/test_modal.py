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

    def _overlay_hyperscript(self, html):
        match = re.search(r'_="([^"]*)"', html)
        self.assertIsNotNone(match)
        return match.group(1)

    def _overlay_tag(self, html):
        match = re.search(r'<div\b[^>]*\bid="modal"[^>]*>', html)
        self.assertIsNotNone(match)
        return match.group(0)

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

    def test_overlay_only_closes_on_click_that_started_on_backdrop(self):
        html = self._render({})
        overlay_hs = self._overlay_hyperscript(html)

        self.assertIn("set :pressedBackdrop to (event.target is me)", overlay_hs)
        self.assertIn("if :pressedBackdrop send closeModal to me end", overlay_hs)

    def test_overlay_closeModal_handler_guards_on_dirty_with_confirm(self):
        html = self._render({})
        overlay_hs = self._overlay_hyperscript(html)

        self.assertIn("on closeModal", overlay_hs)
        self.assertIn("if :dirty", overlay_hs)
        self.assertIn("confirm(@data-dirty-message)", overlay_hs)

        close_index = overlay_hs.index("on closeModal")
        guard_index = overlay_hs.index("if I match .hidden exit end")
        dirty_index = overlay_hs.index("if :dirty")
        self.assertLess(close_index, guard_index)
        self.assertLess(guard_index, dirty_index)

    def test_header_close_button_sends_closeModal(self):
        html = self._render({"id": "modal"})

        self.assertIn('_="on click send closeModal to #modal"', html)

    def test_enable_keyboard_close_false_omits_escape_handler(self):
        html = self._render({"enableKeyboardClose": False})
        overlay_hs = self._overlay_hyperscript(html)

        self.assertNotIn("keydown[key=='Escape']", overlay_hs)

    def test_enable_keyboard_close_default_includes_escape_handler(self):
        html = self._render({})
        overlay_hs = self._overlay_hyperscript(html)

        self.assertIn("keydown[key=='Escape'] from document send closeModal to me", overlay_hs)

    def test_custom_dirty_message_is_rendered(self):
        html = self._render({"dirtyMessage": "Lose your edits?"})
        overlay_tag = self._overlay_tag(html)

        self.assertIn('data-dirty-message="Lose your edits?"', overlay_tag)
        self.assertNotIn("Discard unsaved changes?", overlay_tag)

    def test_default_dirty_message_is_rendered(self):
        html = self._render({})
        overlay_tag = self._overlay_tag(html)

        self.assertIn('data-dirty-message="Discard unsaved changes?"', overlay_tag)

    def test_dirty_message_cannot_inject_hyperscript(self):
        payload = "ok') then fetch('/evil') then confirm('x\" _=\"on click fetch('/evil2')"
        html = self._render({"dirtyMessage": payload})
        overlay_hs = self._overlay_hyperscript(html)
        overlay_tag = self._overlay_tag(html)

        self.assertNotIn("fetch(", overlay_hs)
        self.assertEqual(overlay_tag.count('_="'), 1)
        match = re.search(r'data-dirty-message="([^"]*)"', overlay_tag)
        self.assertIsNotNone(match)
        value = match.group(1)
        self.assertIn("&#34;", value)
        self.assertNotIn('"', value)
        self.assertNotIn("'", value)

    def test_overlay_clears_dirty_on_markModalClean(self):
        html = self._render({})
        overlay_hs = self._overlay_hyperscript(html)

        self.assertIn("on markModalClean set :dirty to false", overlay_hs)

    def test_class_mutation_always_clears_dirty(self):
        html = self._render({})
        overlay_hs = self._overlay_hyperscript(html)

        self.assertIn("on mutation of @class set :dirty to false", overlay_hs)
        self.assertNotIn("on mutation of @class if", overlay_hs)


if __name__ == "__main__":
    unittest.main()
