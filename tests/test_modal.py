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

    def _overlay_tag(self, html):
        match = re.search(r'<div\b[^>]*\bid="modal"[^>]*>', html)
        self.assertIsNotNone(match)
        return match.group(0)

    def _tag_with(self, html, marker):
        match = re.search(rf"<\w+\b[^>]*\b{marker}\b[^>]*>", html)
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

    def test_renders_no_hyperscript(self):
        every_flag = {
            "title": "T",
            "subtitle": "S",
            "icon": "<i></i>",
            "autoOpen": True,
            "showCloseButton": True,
            "enableKeyboardClose": True,
            "enableDirtyGuard": True,
            "footerHtml": "<p>f</p>",
        }
        for params in ({}, every_flag):
            with self.subTest(params=params):
                self.assertNotIn('_="', self._render(params))

    def test_kit_js_hooks_are_on_the_right_elements(self):
        html = self._render({"id": "modal"})

        self.assertIn("data-jui-modal", self._overlay_tag(html))
        self.assertIn(
            'id="modal-content"', self._tag_with(html, "data-jui-modal-content")
        )
        self.assertTrue(
            self._tag_with(html, "data-jui-modal-close").startswith("<button")
        )

    def test_close_button_omitted_when_disabled(self):
        html = self._render({"showCloseButton": False})

        self.assertNotIn("data-jui-modal-close", html)

    def test_keyboard_close_is_on_by_default(self):
        self.assertIn("data-jui-keyboard-close", self._overlay_tag(self._render({})))

    def test_enable_keyboard_close_false_omits_marker(self):
        html = self._render({"enableKeyboardClose": False})

        self.assertNotIn("data-jui-keyboard-close", self._overlay_tag(html))

    def test_dirty_guard_is_off_by_default(self):
        for params in ({}, {"enableDirtyGuard": False, "dirtyMessage": "x"}):
            with self.subTest(params=params):
                overlay_tag = self._overlay_tag(self._render(params))

                self.assertNotIn("data-jui-dirty-guard", overlay_tag)
                self.assertNotIn("data-dirty-message", overlay_tag)

    def test_custom_dirty_message_is_rendered(self):
        html = self._render(
            {"enableDirtyGuard": True, "dirtyMessage": "Lose your edits?"}
        )
        overlay_tag = self._overlay_tag(html)

        self.assertIn("data-jui-dirty-guard", overlay_tag)
        self.assertIn('data-dirty-message="Lose your edits?"', overlay_tag)
        self.assertNotIn("Discard unsaved changes?", overlay_tag)

    def test_default_dirty_message_is_rendered(self):
        html = self._render({"enableDirtyGuard": True})
        overlay_tag = self._overlay_tag(html)

        self.assertIn('data-dirty-message="Discard unsaved changes?"', overlay_tag)

    def test_dirty_message_is_escaped(self):
        payload = "ok\" _=\"on click fetch('/evil')"
        html = self._render({"enableDirtyGuard": True, "dirtyMessage": payload})
        overlay_tag = self._overlay_tag(html)

        self.assertNotIn('_="', overlay_tag)
        match = re.search(r'data-dirty-message="([^"]*)"', overlay_tag)
        self.assertIsNotNone(match)
        self.assertIn("&#34;", match.group(1))


if __name__ == "__main__":
    unittest.main()
