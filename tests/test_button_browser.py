import pytest

TEMPLATE = """
{% from "jinja_ui_kit/components/button/macro.html" import button %}
<form id="f">{{ button(params) }}</form>
"""

COUNT_SUBMITS = """() => {
  window.submits = [];
  document.getElementById('f').addEventListener('submit', (e) => {
    e.preventDefault();
    window.submits.push(e.submitter && e.submitter.disabled);
  });
}"""


@pytest.fixture(
    params=[
        {"text": "Save", "id": "b"},
        {"name": "action", "value": "Save", "id": "b"},
    ],
    ids=["button", "input"],
)
def page(render_page, request):
    page = render_page(TEMPLATE, params={**request.param, "preventDoubleClick": True})
    page.evaluate(COUNT_SUBMITS)
    return page


def state(page):
    return page.evaluate(
        "() => [document.getElementById('b').disabled,"
        " document.getElementById('f').classList.contains('is-submitting')]"
    )


def test_submit_disables_until_after_request(page):
    page.click("#b")

    page.wait_for_function("document.getElementById('b').disabled")
    assert state(page) == [True, True]
    assert page.evaluate("window.submits") == [False]

    page.evaluate(
        "document.getElementById('f')"
        ".dispatchEvent(new CustomEvent('htmx:after:request', {bubbles: true}))"
    )

    assert state(page) == [False, False]
    page.click("#b")
    assert len(page.evaluate("window.submits")) == 2


def test_repeat_click_while_submitting_is_halted(page):
    page.evaluate(
        "() => {"
        " window.clicksSeen = 0;"
        " const b = document.getElementById('b');"
        " b.addEventListener('click', () => window.clicksSeen++);"
        " b.click(); b.click(); b.click();"
        "}"
    )

    assert len(page.evaluate("window.submits")) == 1
    assert page.evaluate("window.clicksSeen") == 1


def test_unguarded_button_is_untouched(render_page):
    page = render_page(TEMPLATE, params={"text": "Save", "id": "b"})
    page.evaluate(COUNT_SUBMITS)

    page.evaluate(
        "() => { const b = document.getElementById('b'); b.click(); b.click(); }"
    )

    assert len(page.evaluate("window.submits")) == 2
    assert state(page) == [False, False]
