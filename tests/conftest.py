import pytest
from jinja2 import Environment, FileSystemLoader, PrefixLoader
from playwright.sync_api import sync_playwright

from jinja_ui_kit.assets import get_css_path, get_js_path


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        yield browser
        browser.close()


@pytest.fixture
def render_page(browser):
    """Load a template snippet into a page with the kit's CSS and JS."""
    env = Environment(
        loader=PrefixLoader(
            {"jinja_ui_kit": FileSystemLoader("src/jinja_ui_kit/templates")}
        ),
        autoescape=True,
    )
    context = browser.new_context()
    context.set_default_timeout(5000)

    def render(source, **params):
        page = context.new_page()
        page.set_content(env.from_string(source).render(**params))
        page.add_style_tag(path=get_css_path())
        page.add_script_tag(path=get_js_path())
        return page

    yield render
    context.close()
