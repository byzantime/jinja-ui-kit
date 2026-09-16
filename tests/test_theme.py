import unittest

from jinja2 import ChoiceLoader, DictLoader, Environment, FileSystemLoader, PrefixLoader

KIT_LOADER = PrefixLoader({"jinja_ui_kit": FileSystemLoader("src/jinja_ui_kit/templates")})


def render(env, source):
    return env.from_string(source).render()


class ThemeDefaultsTests(unittest.TestCase):
    def setUp(self):
        self.env = Environment(loader=KIT_LOADER, autoescape=True)

    def test_start_button_uses_success_variant(self):
        html = render(
            self.env,
            '{% from "jinja_ui_kit/components/button/macro.html" import button %}'
            "{{ button({'text': 'Start', 'isStart': true}) }}",
        )
        self.assertIn("bg-success-600", html)
        self.assertIn("pr-6", html)

    def test_unknown_variant_falls_back_to_primary(self):
        html = render(
            self.env,
            '{% from "jinja_ui_kit/components/button/macro.html" import button %}'
            "{{ button({'text': 'Go', 'variant': 'no-such-variant'}) }}",
        )
        self.assertIn("bg-primary-600", html)

    def test_checkboxes_keep_defaults_without_classes_param(self):
        html = render(
            self.env,
            '{% from "jinja_ui_kit/components/checkboxes/macro.html" import checkboxes %}'
            "{{ checkboxes({'name': 'n', 'items': [{'value': 'a', 'text': 'A'}]}) }}",
        )
        self.assertIn("h-8 w-8", html)


class ThemeOverrideTests(unittest.TestCase):
    """A consumer shadows jinja_ui_kit/theme.html by putting their own loader first."""

    def setUp(self):
        override = PrefixLoader(
            {
                "jinja_ui_kit": DictLoader(
                    {
                        "theme.html": """
{% set textarea = "textarea-custom" %}
{% set input_base = "input-custom" %}
{% set input_border_neutral = "input-border-neutral-custom" %}
{% set input_border_error = "input-border-error-custom" %}
{% set select_base = "select-custom" %}
{% set select_border_neutral = "select-border-neutral-custom" %}
{% set select_border_error = "select-border-error-custom" %}
{% set label_base = "label-custom" %}
{% set accordion_wrapper = "accordion-wrapper-custom" %}
{% set accordion_panel = "accordion-panel-custom" %}
{% set accordion_header_base = "accordion-header-base-custom" %}
{% set accordion_padding_compact = "accordion-padding-compact-custom" %}
{% set accordion_padding_default = "accordion-padding-default-custom" %}
{% set accordion_content_base = "accordion-content-base-custom" %}
{% set accordion_title = "accordion-title-custom" %}
{% set accordion_chevron = "accordion-chevron-custom" %}
{% set details_wrapper = "details-wrapper-custom" %}
{% set details_summary = "details-summary-custom" %}
{% set details_chevron = "details-chevron-custom" %}
{% set details_content = "details-content-custom" %}
{% set error_summary_wrapper = "error-summary-wrapper-custom" %}
{% set error_summary_heading = "error-summary-heading-custom" %}
{% set error_summary_list = "error-summary-list-custom" %}
"""
                    }
                )
            }
        )
        self.env = Environment(
            loader=ChoiceLoader([override, KIT_LOADER]), autoescape=True
        )

    def test_shadowed_theme_replaces_textarea_defaults(self):
        html = render(
            self.env,
            '{% from "jinja_ui_kit/components/textarea/macro.html" import textarea %}'
            "{{ textarea({'name': 'notes', 'label': {'text': 'Notes'}}) }}",
        )
        self.assertIn("textarea-custom", html)
        self.assertNotIn("font-mono", html)

    def test_shadowed_theme_replaces_input_defaults(self):
        html = render(
            self.env,
            '{% from "jinja_ui_kit/components/input/macro.html" import input %}'
            "{{ input({'name': 'username', 'label': {'text': 'Username'}}) }}",
        )
        self.assertIn("input-custom", html)
        self.assertIn("input-border-neutral-custom", html)
        self.assertNotIn("focus:ring-primary-500", html)

    def test_shadowed_theme_replaces_input_error_variant(self):
        html = render(
            self.env,
            '{% from "jinja_ui_kit/components/input/macro.html" import input %}'
            "{{ input({'name': 'username', 'label': {'text': 'Username'}, "
            "'errorMessage': {'text': 'Required'}}) }}",
        )
        self.assertIn("input-border-error-custom", html)

    def test_shadowed_theme_replaces_select_defaults(self):
        html = render(
            self.env,
            '{% from "jinja_ui_kit/components/select/macro.html" import select %}'
            "{{ select({'name': 'color', 'items': []}) }}",
        )
        self.assertIn("select-custom", html)
        self.assertIn("select-border-neutral-custom", html)
        self.assertNotIn("focus:ring-primary-500", html)

    def test_shadowed_theme_replaces_select_error_variant(self):
        html = render(
            self.env,
            '{% from "jinja_ui_kit/components/select/macro.html" import select %}'
            "{{ select({'name': 'color', 'items': [], "
            "'errorMessage': {'text': 'Required'}}) }}",
        )
        self.assertIn("select-border-error-custom", html)

    def test_shadowed_theme_replaces_label_defaults(self):
        html = render(
            self.env,
            '{% from "jinja_ui_kit/components/label/macro.html" import label %}'
            "{{ label({'text': 'Username', 'for': 'username'}) }}",
        )
        self.assertIn("label-custom", html)
        self.assertNotIn("text-neutral-700", html)

    def test_shadowed_theme_replaces_accordion_defaults(self):
        html = render(
            self.env,
            '{% from "jinja_ui_kit/components/accordion/macro.html" import accordion %}'
            "{{ accordion({'sections': [{'title': 'T', 'content': 'C'}]}) }}",
        )
        self.assertIn("accordion-wrapper-custom", html)
        self.assertIn("accordion-panel-custom", html)
        self.assertIn("accordion-header-base-custom", html)
        self.assertIn("accordion-padding-default-custom", html)
        self.assertIn("accordion-content-base-custom", html)
        self.assertIn("accordion-title-custom", html)
        self.assertIn("accordion-chevron-custom", html)
        self.assertNotIn("space-y-1", html)
        self.assertNotIn("border-neutral-200", html)
        self.assertNotIn("rounded-lg", html)
        self.assertNotIn("p-4", html)
        self.assertNotIn("text-sm", html)

    def test_shadowed_theme_replaces_accordion_compact_padding(self):
        html = render(
            self.env,
            '{% from "jinja_ui_kit/components/accordion/macro.html" import accordion %}'
            "{{ accordion({'sections': [{'title': 'T', 'content': 'C'}], 'compact': true}) }}",
        )
        self.assertIn("accordion-padding-compact-custom", html)
        self.assertNotIn("py-2 px-3", html)

    def test_shadowed_theme_replaces_details_defaults(self):
        html = render(
            self.env,
            '{% from "jinja_ui_kit/components/details/macro.html" import details %}'
            "{{ details({'summaryText': 'S', 'text': 'B'}) }}",
        )
        self.assertIn("details-wrapper-custom", html)
        self.assertIn("details-summary-custom", html)
        self.assertIn("details-chevron-custom", html)
        self.assertIn("details-content-custom", html)
        self.assertNotIn("[&::-webkit-details-marker]:hidden", html)
        self.assertNotIn("px-4", html)
        self.assertNotIn("border-neutral-200", html)
        self.assertNotIn("group w-full", html)

    def test_shadowed_theme_replaces_error_summary_defaults(self):
        html = render(
            self.env,
            '{% from "jinja_ui_kit/components/error-summary/macro.html" import errorSummary %}'
            "{{ errorSummary({'titleText': 'There is a problem', "
            "'errorList': [{'text': 'E'}]}) }}",
        )
        self.assertIn("error-summary-wrapper-custom", html)
        self.assertIn("error-summary-heading-custom", html)
        self.assertIn("error-summary-list-custom", html)
        self.assertNotIn("border-l-4", html)
        self.assertNotIn("p-4", html)
        self.assertNotIn("mb-6", html)
        self.assertNotIn("pl-5", html)


if __name__ == "__main__":
    unittest.main()
