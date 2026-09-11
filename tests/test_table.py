from jinja2 import Environment, FileSystemLoader, PrefixLoader, UndefinedError
import re
import unittest


class StickyHeaderTableMacroTests(unittest.TestCase):
    def _render(self, params):
        env = Environment(
            loader=PrefixLoader(
                {"jinja_ui_kit": FileSystemLoader("src/jinja_ui_kit/templates")}
            ),
            autoescape=True,
        )
        template = env.from_string(
            """
            {% from "jinja_ui_kit/components/table/macro.html" import sticky_header_table %}
            {{ sticky_header_table(params) }}
            """
        )
        return template.render(params=params)

    def _row_hyperscript(self, html):
        match = re.search(r'<tr[^>]*_="([^"]*)"', html)
        self.assertIsNotNone(match)
        return match.group(1)

    def _clickable_params(self, row_id, **overrides):
        params = {
            "head": [{"text": "Name"}],
            "rows": [{"id": row_id, "cells": [{"text": "Alice"}]}],
            "clickableRows": True,
        }
        params.update(overrides)
        return params

    def test_hostile_row_id_stays_in_autoescaped_data_attribute(self):
        hostile = "x') then fetch('/evil') then trigger openModal('"
        html = self._render(
            self._clickable_params(hostile, rowClickEvent="openModal")
        )

        self.assertIn('data-row-id="x&#39;) then fetch(&#39;/evil&#39;) then trigger openModal(&#39;"', html)
        self.assertEqual(
            self._row_hyperscript(html),
            "on click trigger openModal(rowId: @data-row-id)",
        )
        self.assertNotIn("fetch(", self._row_hyperscript(html))

    def test_default_row_click_event_is_spliced(self):
        html = self._render(self._clickable_params("row-1"))

        self.assertIn("on click trigger rowClicked(rowId: @data-row-id)", html)

    def test_custom_row_click_event_is_spliced(self):
        html = self._render(
            self._clickable_params("row-1", rowClickEvent="openModal")
        )

        self.assertIn("on click trigger openModal(rowId: @data-row-id)", html)

    def test_non_clickable_rows_omit_handler_and_data_attribute(self):
        html = self._render(
            {
                "head": [{"text": "Name"}],
                "rows": [{"id": "row-1", "cells": [{"text": "Alice"}]}],
            }
        )

        self.assertNotIn("_=", html)
        self.assertNotIn("data-row-id", html)

    def test_colon_namespaced_row_click_event_is_accepted(self):
        html = self._render(
            self._clickable_params("row-1", rowClickEvent="foo:bar")
        )

        self.assertIn("on click trigger foo:bar(rowId: @data-row-id)", html)

    def test_invalid_row_click_event_raises_with_explanatory_message(self):
        for bad in ("bad-name", "9bad", "o'pen", ""):
            with self.subTest(bad=bad):
                with self.assertRaises(UndefinedError) as ctx:
                    self._render(self._clickable_params("row-1", rowClickEvent=bad))
                self.assertIn("rowClickEvent must match", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
