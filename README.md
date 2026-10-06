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

**If your project uses Tailwind CSS (recommended)**

Add jinja-ui-kit's templates to your Tailwind content scan so all needed utility classes are compiled into your single project build. Because the template path is only knowable at Python runtime, generate a small JS shim as a build step and add it to `.gitignore`:

```bash
# In your build script (e.g. local_build.sh), before running tailwindcss:
python -c "from jinja_ui_kit.assets import write_tailwind_content; write_tailwind_content()"
```

Then require it in `tailwind.config.js`:

```js
const { content: kitContent } = require('./jinja_ui_kit_tailwind.js');

module.exports = {
  content: [
    "./src/templates/**/*.html",
    ...kitContent,
  ],
};
```

Add the generated file to `.gitignore` — it contains a machine-specific absolute path and should be regenerated on each environment setup:

```
jinja_ui_kit_tailwind.js
```

This approach avoids shipping two separate Tailwind builds, which can cause cascade conflicts where duplicate utility class definitions override each other depending on bundle order.

**If your project does not use Tailwind CSS**

jinja-ui-kit ships a pre-compiled CSS file containing all necessary classes. Include it in your asset pipeline before your own styles:

```python
from quart_assets import Bundle, QuartAssets
from jinja_ui_kit.assets import get_css_path

assets = QuartAssets(app)

css_bundle = Bundle(
    get_css_path(),        # jinja-ui-kit styles
    "css/your-app.css",    # your application styles
    output="css/packed-%(version)s.min.css",
)

assets.register("css_all", css_bundle)
```

Or with a direct `<link>` tag:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/jinja-ui-kit.min.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/your-app.css') }}">
```

### 3. Include JS

The modal and button macros get their behaviour (closing modals, the dirty guard, `preventDoubleClick`) from a small vanilla JS file shipped with the kit. Its listeners are delegated from `document`, so markup swapped in by htmx needs no extra processing. Add it to every page that renders those macros, either in your asset bundle:

```python
from jinja_ui_kit.assets import get_js_path

js_bundle = Bundle(get_js_path(), "js/your-app.js", output="js/packed-%(version)s.js")
```

or as a script tag (it is safe in `<head>` with `defer`):

```html
<script defer src="{{ url_for('static', filename='js/jinja-ui-kit.js') }}"></script>
```

### Upgrading to 0.3

- Include the kit's JS (step 3 above). Without it, modals no longer close and `preventDoubleClick` does nothing.
- The modal and button macros no longer emit hyperscript (`_="…"`), so they no longer need `_hyperscript`. The accordion, radios, checkboxes and table macros still do.
- The `closeModal` / `markModalClean` events work as before. A Cancel button inside a modal can carry `data-jui-modal-close` instead of `_="on click send closeModal to #id"`.
- With `preventDoubleClick`, a caller's `attributes._` is no longer merged with a guard script; it is emitted exactly as given.

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
- **Checkboxes** - Multiple checkbox inputs with proper labeling and conditional reveal support
- **Radios** - Radio button groups with proper labeling and conditional reveal support
- **Date Input** - Three-part day/month/year date entry with fieldset, hint and error support
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
{% from "jinja_ui_kit/components/checkboxes/macro.html" import checkboxes %}
{% from "jinja_ui_kit/components/radios/macro.html" import radios %}

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

<!-- Checkboxes -->
{{ checkboxes({
  'name': 'contact',
  'fieldset': {
    'legend': {
      'text': 'How would you like to be contacted?'
    }
  },
  'items': [
    {
      'value': 'email',
      'text': 'Email'
    },
    {
      'value': 'phone',
      'text': 'Phone'
    }
  ]
}) }}

<!-- Radios -->
{{ radios({
  'name': 'contact-method',
  'fieldset': {
    'legend': {
      'text': 'How would you prefer to be contacted?'
    }
  },
  'items': [
    {
      'value': 'email',
      'text': 'Email'
    },
    {
      'value': 'phone',
      'text': 'Phone'
    },
    {
      'value': 'text',
      'text': 'Text message'
    }
  ]
}) }}
```

## Development

```bash
# Rebuild CSS after making changes
tailwindcss -i ./src/styles/input.css -o ./src/jinja_ui_kit/dist/jinja-ui-kit.min.css --minify

# Run the tests (the browser tests need Chromium's headless shell)
uv sync
uv run playwright install chromium-headless-shell
uv run pytest

# Lint and format-check the JS (ESLint + Prettier, as CI runs them)
npm ci
npm run lint
npm run format:check   # `npm run format` rewrites in place
```

`dist/jinja-ui-kit.js` is hand-written and shipped as-is; there is no build step for it.

## Theming

Components don't reference raw Tailwind palette classes (`blue-600`, `red-600`, etc.) directly. Instead they use a small set of semantic color tokens defined in this package's `tailwind.config.js`:

| Token | Default palette | Used for |
|---|---|---|
| `primary` | `blue` | Primary buttons, links, focus rings |
| `danger` | `red` | Errors, warning buttons |
| `success` | `green` | Start/success buttons |
| `neutral` | `gray` | Borders, backgrounds, secondary text |

Each token supports the full `50`–`900` shade scale (e.g. `bg-primary-600`, `text-primary-700`), matching how you'd use any built-in Tailwind color.

**If your project uses Tailwind CSS** (see [Include CSS Styles](#2-include-css-styles) above), you already share jinja-ui-kit's template content with your own Tailwind build. To restyle jinja-ui-kit's components, add or override these token names in your own `tailwind.config.js` — no changes to jinja-ui-kit's Python or templates are needed, since only content globs are shared, not jinja-ui-kit's theme:

```js
// your app's tailwind.config.js
module.exports = {
  content: [
    "./src/templates/**/*.html",
    ...kitContent, // jinja-ui-kit's templates, from the content-glob shim
  ],
  theme: {
    extend: {
      colors: {
        // Override jinja-ui-kit's "primary" token with your brand color,
        // using the same 50-900 shade scale.
        primary: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
          700: '#7e22ce',
          800: '#6b21a8',
          900: '#581c87',
        },
        // danger, success, and neutral can be overridden the same way
      },
    },
  },
};
```

Because Tailwind compiles utility classes on demand from your build's content scan, overriding `primary` here changes the color of every `bg-primary-*`/`text-primary-*`/`border-primary-*`/`ring-primary-*` class jinja-ui-kit's templates use — including buttons, focus rings, and links — without touching Tailwind's own `blue` palette or repainting unrelated uses of blue elsewhere in your app.

### Non-colour defaults: `theme.html`

Every non-colour default — spacing, control sizes, border radius, fonts, button variants — lives as a named value in a single template, [`jinja_ui_kit/theme.html`](src/jinja_ui_kit/templates/theme.html), which the component macros import. To change any of them, shadow that file: copy the shipped one into your own templates, edit it, and map it in a loader placed *before* jinja-ui-kit's:

```python
app.jinja_loader = ChoiceLoader([
    PrefixLoader({
        # Contains your edited copy as theme.html
        "jinja_ui_kit": FileSystemLoader("src/templates/jinja_ui_kit_overrides"),
    }),
    PrefixLoader({
        "jinja_ui_kit": PackageLoader("jinja_ui_kit"),
    }),
    app.jinja_loader,
])
```

Always start from a full copy of the shipped file: a key missing from your override renders as an empty string, not as the kit default. Per-call-site `params.classes` still *appends* to these defaults — wholesale replacement happens in `theme.html`, not per call.

### Semantic hooks and the optional semantic layer

Form components emit stable semantic classes: `.form-group`, `.form-group--error`, `.textarea__wrapper`, `.file-upload__wrapper`. The kit ships modest default styles for them in `styles/semantic.css` (field spacing, error accent). Tailwind consumers opt in with a generated shim (same pattern as the content glob):

```bash
python -c "from jinja_ui_kit.assets import write_semantic_css_import; write_semantic_css_import()"
```

then at the top of your Tailwind input CSS, before the `@tailwind` directives:

```css
@import "./jinja_ui_kit_semantic.css";
```

Add `jinja_ui_kit_semantic.css` to `.gitignore`. The rules compile against *your* theme tokens and are plain `@layer components` styles, so you can override them by normal cascade — or skip the import and define the hooks yourself.

### If your project does not use Tailwind CSS

The pre-compiled `jinja-ui-kit.min.css` is a frozen snapshot of the defaults: the default palette *and* the default `theme.html` classes, semantic layer included. Remapping colour tokens or shadowing `theme.html` with classes outside that snapshot requires the Tailwind route above (or forking the build — see [Development](#development)); the dist file suits projects happy with the kit's look as-is.

## Design Philosophy

This library follows the GOV.UK Frontend approach of:
- Accessible, semantic HTML
- Consistent component APIs
- Flexible configuration through parameter objects
- Separation of structure and styling

All components use Tailwind CSS classes for styling and include proper ARIA attributes for accessibility.

## License

MIT License
