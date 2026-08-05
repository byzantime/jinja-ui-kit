import re
import unittest

from jinja2 import Environment, FileSystemLoader, PrefixLoader


class DateInputMacroTests(unittest.TestCase):
    def _render(self, params):
        env = Environment(
            loader=PrefixLoader(
                {"jinja_ui_kit": FileSystemLoader("src/jinja_ui_kit/templates")}
            ),
            autoescape=True,
        )
        template = env.from_string(
            """
            {% from "jinja_ui_kit/components/date-input/macro.html" import dateInput %}
            {{ dateInput(params) }}
            """
        )
        return template.render(params=params)

    def test_default_items_render_three_named_inputs(self):
        html = self._render(
            {
                "namePrefix": "dob",
                "fieldset": {"legend": {"text": "Date of birth"}},
                "hint": {"text": "For example, 27 3 2007"},
            }
        )

        for suffix in ("day", "month", "year"):
            self.assertIn('name="dob-%s"' % suffix, html)
            self.assertIn('id="dob-%s"' % suffix, html)

    def test_default_items_are_labelled_and_wrapped_in_fieldset(self):
        html = self._render(
            {
                "namePrefix": "dob",
                "fieldset": {"legend": {"text": "Date of birth"}},
            }
        )

        self.assertIn("<fieldset", html)
        self.assertIn("Date of birth", html)
        self.assertIn('for="dob-day"', html)
        self.assertIn('for="dob-month"', html)
        self.assertIn('for="dob-year"', html)
        self.assertRegex(html, r'for="dob-day">\s*Day\s*</label>')
        self.assertRegex(html, r'for="dob-month">\s*Month\s*</label>')
        self.assertRegex(html, r'for="dob-year">\s*Year\s*</label>')

    def test_hint_is_referenced_via_aria_describedby(self):
        html = self._render(
            {
                "namePrefix": "dob",
                "fieldset": {"legend": {"text": "Date of birth"}},
                "hint": {"text": "For example, 27 3 2007"},
            }
        )

        self.assertIn('id="dob-hint"', html)
        # Fieldset and every input should reference the hint.
        self.assertEqual(html.count('aria-describedby="dob-hint"'), 4)
        self.assertIn('role="group"', html)

    def test_error_message_appended_to_describedby(self):
        html = self._render(
            {
                "id": "dob",
                "namePrefix": "dob",
                "hint": {"text": "For example, 27 3 2007"},
                "errorMessage": {"text": "Enter a date of birth"},
            }
        )

        self.assertIn('id="dob-error"', html)
        self.assertIn('aria-describedby="dob-hint dob-error"', html)

    def test_custom_items_override_defaults(self):
        html = self._render(
            {
                "namePrefix": "created",
                "items": [
                    {"label": {"text": "Month"}, "name": "month"},
                    {"label": {"text": "Year"}, "name": "year"},
                ],
            }
        )

        self.assertIn('name="created-month"', html)
        self.assertIn('name="created-year"', html)
        self.assertNotIn('name="created-day"', html)

    def test_inputmode_defaults_to_numeric(self):
        html = self._render({"namePrefix": "dob"})
        self.assertEqual(html.count('inputmode="numeric"'), 3)

    def test_id_defaults_to_name_prefix(self):
        html = self._render({"namePrefix": "dob"})
        self.assertIn('id="dob-day"', html)

    def test_year_input_is_wider_than_day(self):
        html = self._render({"namePrefix": "dob"})
        day = re.search(r'<input[^>]*id="dob-day"[^>]*>', html).group(0)
        year = re.search(r'<input[^>]*id="dob-year"[^>]*>', html).group(0)
        self.assertIn("w-16", day)
        self.assertIn("w-24", year)


if __name__ == "__main__":
    unittest.main()
