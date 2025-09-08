# Jinja UI Kit

A collection of reusable Jinja2 macros for building web application UIs with Tailwind CSS styling, heavily inspired by govuk-frontend-jinja.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/byzantime/jinja-ui-kit.git
```

Or add to your requirements file:

```
jinja-ui-kit @ git+https://github.com/byzantime/jinja-ui-kit.git
```

## Setup

### 1. Configure Template Loading

**For Flask/Quart applications:**

Configure your Jinja2 loader to include jinja-ui-kit templates:

```python
from quart import Quart
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

app = Quart(__name__)

# Configure Jinja loader to include jinja-ui-kit
app.jinja_loader = ChoiceLoader([
    PrefixLoader({
        "jinja_ui_kit": PackageLoader("jinja_ui_kit"),
    }),
    app.jinja_loader,  # Keep the default loader
])
```

### 2. Include CSS Styles

jinja-ui-kit provides a pre-compiled CSS file containing all necessary Tailwind classes. Include it in your asset pipeline:

**With asset bundling (Quart-Assets, Flask-Assets, etc.):**

```python
from quart_assets import Bundle, QuartAssets
from jinja_ui_kit.assets import get_css_path

assets = QuartAssets(app)

css_bundle = Bundle(
    get_css_path(),  # jinja-ui-kit styles first
    "css/your-app.css",  # Your application styles
    "css/other-styles.css",
    output="css/packed-%(version)s.min.css",
)

assets.register("css_all", css_bundle)
```

**With direct HTML link tag:**

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/jinja-ui-kit.min.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/your-app.css') }}">
```

## Usage

Import components in your Jinja2 templates:

```jinja2
{% from "jinja_ui_kit/components/button/macro.html" import button %}
{% from "jinja_ui_kit/components/input/macro.html" import input %}

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
- **Button** - Configurable buttons with multiple variants (primary, secondary, warning, inverse, start)
- **Input** - Text inputs with label, hint, and error support
- **Textarea** - Multi-line text inputs
- **Select** - Dropdown select inputs
- **Checkbox** - Checkbox inputs with proper labeling
- **File Upload** - File input with drag-and-drop styling

### UI Components
- **Accordion** - Collapsible content sections
- **Table** - Data tables with sticky headers
- **Error Summary** - Form error summaries for validation feedback
- **Error Message** - Individual field error messages
- **Hint** - Helper text for form fields
- **Label** - Form field labels

### Utilities
- **Attributes** - HTML attribute rendering utility

## Component Examples

### Button Variants

```jinja2
{% from "jinja_ui_kit/components/button/macro.html" import button %}

<!-- Primary button (default) -->
{{ button({"text": "Continue"}) }}

<!-- Secondary button -->
{{ button({
  'text': 'Cancel',
  'variant': 'secondary'
}) }}

<!-- Warning button -->
{{ button({
  'text': 'Delete account',
  'variant': 'warning'
}) }}

<!-- Start button with arrow -->
{{ button({
  'text': 'Start now',
  'href': '/start',
  'isStart': true
}) }}

<!-- Disabled button -->
{{ button({
  'text': 'Submit',
  'disabled': true
}) }}
```

### Form Components

```jinja2
{% from "jinja_ui_kit/components/input/macro.html" import input %}
{% from "jinja_ui_kit/components/textarea/macro.html" import textarea %}
{% from "jinja_ui_kit/components/select/macro.html" import select %}
{% from "jinja_ui_kit/components/checkbox/macro.html" import checkbox %}

<!-- Text input with validation -->
{{ input({
  'name': "email",
  'type': "email",
  'value': form.email.data,
  'label': {"text": "Email address"},
  'hint': {"text": "We'll use this to contact you"},
  'errorMessage': {"text": "Enter a valid email address"} if form.email.errors else none
}) }}

<!-- Textarea -->
{{ textarea({
  'name': "description",
  'label': {"text": "Description"},
  'hint': {"text": "Provide additional details"},
  'rows': 5
}) }}

<!-- Select dropdown -->
{{ select({
  'name': "country",
  'label': {"text": "Country"},
  'items': [
    {"value": "", "text": "Choose country"},
    {"value": "ru", "text": "Russia"},
    {"value": "cn", "text": "China"},
    {"value": "us", "text": "United States"},
  ]
}) }}

<!-- Checkbox -->
{{ checkbox({
  'name': "subscribe",
  'label': {"text": "Subscribe to newsletter"},
  'hint': {"text": "Get updates about new features"}
}) }}
```

## Design Philosophy

This library follows the GOV.UK Frontend approach of:
- Accessible, semantic HTML
- Consistent component APIs
- Flexible configuration through parameter objects
- Separation of structure and styling

All components use Tailwind CSS classes for styling and include proper ARIA attributes for accessibility.

## License

MIT License
