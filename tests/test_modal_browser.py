import pytest

TEMPLATE = """
{% from "jinja_ui_kit/components/modal/macro.html" import modal %}
{% call modal(params) %}
  <input id="field">
  <button type="button" id="inner">Inner</button>
  <button type="button" id="cancel" data-jui-modal-close>Cancel</button>
{% endcall %}
"""

LISTEN_ON_BODY = """() => {
  window.bodyClicks = 0;
  window.closesSeen = [];
  document.body.addEventListener('click', () => window.bodyClicks++);
  document.body.addEventListener('closeModal', (e) => {
    window.closesSeen.push(e.target.classList.contains('hidden'));
  });
}"""


@pytest.fixture
def open_modal(render_page):
    def open_modal(**params):
        page = render_page(TEMPLATE, params={"id": "m", "autoOpen": True, **params})
        page.evaluate(LISTEN_ON_BODY)
        page.dialogs = []

        def on_dialog(dialog):
            page.dialogs.append(dialog.message)
            if page.accept_dialogs:
                dialog.accept()
            else:
                dialog.dismiss()

        page.accept_dialogs = False
        page.on("dialog", on_dialog)
        return page

    return open_modal


def is_open(page):
    return page.evaluate("() => !document.getElementById('m').matches('.hidden')")


def send(page, event, bubbles=True):
    page.evaluate(
        "([event, bubbles]) => document.getElementById('m')"
        ".dispatchEvent(new CustomEvent(event, {bubbles}))",
        [event, bubbles],
    )


def test_backdrop_click_closes(open_modal):
    page = open_modal()

    page.mouse.click(5, 5)

    assert not is_open(page)
    assert page.evaluate("document.getElementById('m').matches('.flex')") is False
    assert page.evaluate("window.closesSeen") == [True]


def test_drag_from_content_to_backdrop_does_not_close(open_modal):
    page = open_modal()
    box = page.locator("#m-content").bounding_box()

    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.mouse.down()
    page.mouse.move(5, 5)
    page.mouse.up()

    assert is_open(page)


def test_click_inside_content_reaches_target_but_not_body(open_modal):
    page = open_modal()
    page.evaluate(
        "window.innerClicks = 0;"
        "document.getElementById('inner')"
        ".addEventListener('click', () => window.innerClicks++)"
    )

    page.click("#inner")
    page.click("#inner")

    assert page.evaluate("window.innerClicks") == 2
    assert page.evaluate("window.bodyClicks") == 0
    assert is_open(page)


def test_close_buttons_close(open_modal):
    for selector in ("#m-content button:has(i.fa-times)", "#cancel"):
        page = open_modal(title="T")
        page.add_style_tag(content=".fa-times::before { content: 'x'; }")

        page.click(selector)

        assert not is_open(page)
        assert page.evaluate("window.closesSeen") == [True]


def test_escape_closes_only_with_keyboard_close(open_modal):
    page = open_modal()
    page.keyboard.press("Escape")
    assert not is_open(page)

    page = open_modal(enableKeyboardClose=False)
    page.keyboard.press("Escape")
    assert is_open(page)


@pytest.mark.parametrize("bubbles", [True, False])
def test_dispatched_closeModal_closes_before_body_sees_it(open_modal, bubbles):
    page = open_modal()

    send(page, "closeModal", bubbles=bubbles)

    assert not is_open(page)
    assert page.evaluate("window.closesSeen") == ([True] if bubbles else [])


def test_closeModal_on_hidden_modal_is_noop(open_modal):
    page = open_modal(autoOpen=False, enableDirtyGuard=True)

    send(page, "closeModal")

    assert page.dialogs == []
    assert page.evaluate("document.getElementById('m').className").count("hidden") == 1


def test_dirty_guard_dismissed_confirm_keeps_modal_open(open_modal):
    page = open_modal(enableDirtyGuard=True, dirtyMessage="Lose edits?")
    page.fill("#field", "x")

    send(page, "closeModal")

    assert page.dialogs == ["Lose edits?"]
    assert is_open(page)
    assert page.evaluate("window.closesSeen") == []


def test_dirty_guard_accepted_confirm_closes(open_modal):
    page = open_modal(enableDirtyGuard=True)
    page.accept_dialogs = True
    page.fill("#field", "x")

    page.keyboard.press("Escape")

    assert page.dialogs == ["Discard unsaved changes?"]
    assert not is_open(page)
    assert page.evaluate("window.closesSeen") == [True]


def test_markModalClean_clears_dirty(open_modal):
    page = open_modal(enableDirtyGuard=True)
    page.fill("#field", "x")

    send(page, "markModalClean", bubbles=False)
    send(page, "closeModal")

    assert page.dialogs == []
    assert not is_open(page)


def test_reopening_clears_dirty(open_modal):
    page = open_modal(enableDirtyGuard=True)
    page.fill("#field", "x")
    page.evaluate(
        "const m = document.getElementById('m');"
        "m.classList.add('hidden'); m.classList.remove('flex');"
    )
    page.evaluate(
        "const m = document.getElementById('m');"
        "m.classList.remove('hidden'); m.classList.add('flex');"
    )

    send(page, "closeModal")

    assert page.dialogs == []
    assert not is_open(page)


def test_edits_without_guard_never_prompt(open_modal):
    page = open_modal()
    page.fill("#field", "x")

    send(page, "closeModal")

    assert page.dialogs == []
    assert not is_open(page)
