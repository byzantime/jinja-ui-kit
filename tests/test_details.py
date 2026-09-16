import re
import unittest

from jinja2 import Environment, FileSystemLoader, PrefixLoader


class DetailsMacroTests(unittest.TestCase):
    def _env(self):
        return Environment(
            loader=PrefixLoader(
                {"jinja_ui_kit": FileSystemLoader("src/jinja_ui_kit/templates")}
            ),
            autoescape=True,
        )

    def _render(self, params):
        template = self._env().from_string(
            """
            {% from "jinja_ui_kit/components/details/macro.html" import details %}
            {{ details(params) }}
            """
        )
        return template.render(params=params)

    def _render_call(self, params, body="<p>Caller body</p>"):
        template = self._env().from_string(
            '{% from "jinja_ui_kit/components/details/macro.html" import details %}'
            "{% call details(params) %}" + body + "{% endcall %}"
        )
        return template.render(params=params)

    def _details_tag(self, html):
        match = re.search(r"<details\b[^>]*>", html)
        self.assertIsNotNone(match)
        return match.group(0)

    def test_default_render_is_closed(self):
        html = self._render({"summaryText": "Help with nationality"})

        tag = self._details_tag(html)
        self.assertNotIn(" open", tag)
        self.assertIn("<summary", html)

    def test_open_true_renders_open_attribute(self):
        html = self._render({"summaryText": "Help with nationality", "open": True})

        self.assertIn(" open", self._details_tag(html))

    def test_open_falsey_values_are_omitted(self):
        for value in (False, 0, "", []):
            with self.subTest(open=value):
                html = self._render({"summaryText": "Summary", "open": value})

                self.assertNotIn(" open", self._details_tag(html))

    def test_empty_id_is_omitted(self):
        html = self._render({"id": "", "summaryText": "Summary"})

        self.assertNotIn("id=", self._details_tag(html))

    def test_summary_text_is_escaped(self):
        html = self._render({"summaryText": "<b>Help</b>", "text": "Body"})

        self.assertIn("&lt;b&gt;Help&lt;/b&gt;", html)
        self.assertNotIn("<b>Help</b>", html)

    def test_summary_html_is_rendered_raw(self):
        html = self._render({"summaryHtml": "<b>Help</b>", "text": "Body"})

        self.assertIn("<b>Help</b>", html)

    def test_text_body_is_escaped(self):
        html = self._render({"summaryText": "Summary", "text": "<b>Body</b>"})

        self.assertIn("&lt;b&gt;Body&lt;/b&gt;", html)

    def test_html_body_is_rendered_raw(self):
        html = self._render({"summaryText": "Summary", "html": "<b>Body</b>"})

        self.assertIn("<b>Body</b>", html)

    def test_caller_body_takes_precedence_over_text_and_html(self):
        html = self._render_call(
            {"summaryText": "Summary", "text": "Ignored text", "html": "<b>Ignored</b>"},
            body="<p>Caller wins</p>",
        )

        self.assertIn("<p>Caller wins</p>", html)
        self.assertNotIn("Ignored text", html)
        self.assertNotIn("<b>Ignored</b>", html)

    def test_classes_are_appended_to_details(self):
        html = self._render({"summaryText": "Summary", "classes": "my-custom-class"})

        tag = self._details_tag(html)
        self.assertIn("group", tag)
        self.assertIn("my-custom-class", tag)

    def test_attributes_are_passed_through_to_details(self):
        html = self._render(
            {"summaryText": "Summary", "attributes": {"data-foo": "bar"}}
        )

        self.assertIn('data-foo="bar"', self._details_tag(html))

    def test_id_is_rendered_on_details(self):
        html = self._render({"id": "my-details", "summaryText": "Summary"})

        self.assertIn('id="my-details"', self._details_tag(html))

    def test_chevron_uses_native_open_state(self):
        html = self._render({"summaryText": "Summary"})

        self.assertIn("group-open:rotate-180", html)


if __name__ == "__main__":
    unittest.main()
