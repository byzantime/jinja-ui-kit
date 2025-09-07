# Jinja UI Kit

A collection of reusable Jinja2 macros for building web application UIs with Tailwind CSS styling, heavily inspired by govuk-frontend-jinja.

## Installation (if you must)

Install directly from GitHub:

```bash
pip install git+https://github.com/byzantime/jinja-ui-kit.git
```

Or add to your requirements file:

```
jinja-ui-kit @ git+https://github.com/byzantime/jinja-ui-kit.git
```

## Usage

Import components in your Jinja2 templates:

```jinja2
{% from "jinja_ui_kit/templates/components/button/macro.html" import button %}
{% from "jinja_ui_kit/templates/components/input/macro.html" import input %}

{{ button({
  "text": "Continue",
  "variant": "primary"
}) }}

{{ input({
  "name": "email",
  "type": "email",
  "label": {
    "text": "Email address"
  },
  "hint": {
    "text": "We'll use this to send you updates"
  }
}) }}
```

## Available Components

### Form Components
- **Button** - Configurable buttons with multiple variants
- **Input** - Text inputs with label, hint, and error support
- **Textarea** - Multi-line text inputs
- **Select** - Dropdown select inputs
- **Checkbox** - Checkbox inputs
- **File Upload** - File input with drag-and-drop styling

### UI Components
- **Accordion** - Collapsible content sections
- **Table** - Data tables with sticky headers
- **Error Summary** - Form error summaries
- **Error Message** - Individual field errors
- **Hint** - Helper text for form fields
- **Label** - Form field labels

### Utilities
- **Attributes** - HTML attribute rendering utility

## Design Philosophy

This library follows the GOV.UK Frontend approach of:
- Accessible, semantic HTML
- Consistent component APIs
- Flexible configuration through parameter objects
- Separation of structure and styling

All components use Tailwind CSS classes for styling and include proper ARIA attributes for accessibility.

## License

MIT License
