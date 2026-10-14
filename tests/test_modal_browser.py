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
  document.body.addEventListener('closeModal', () => {
    window.closesSeen.push(document.getElementById('m').matches('.hidden'));
  });
}"""


@pytest.fixture
def open_modal(render_page):
    def open_modal(**params):
        page = render_page(TEMPLATE, params={"id": "m", "autoOpen": True, **params})
        page.evaluate(LISTEN_ON_BODY)
        record_dialogs(page)
        return page

    return open_modal


def record_dialogs(page):
    page.dialogs = []

    def on_dialog(dialog):
        page.dialogs.append(dialog.message)
        if page.accept_dialogs:
            dialog.accept()
        else:
            dialog.dismiss()

    page.accept_dialogs = False
    page.on("dialog", on_dialog)


def is_open(page):
    return page.evaluate("() => !document.getElementById('m').matches('.hidden')")


def send(page, event, bubbles=True, selector="#m"):
    page.evaluate(
        "([selector, event, bubbles]) => document.querySelector(selector)"
        ".dispatchEvent(new CustomEvent(event, {bubbles}))",
        [selector, event, bubbles],
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


def test_closeModal_from_descendant_closes_before_body_sees_it(open_modal):
    page = open_modal()

    send(page, "closeModal", selector="#inner")

    assert not is_open(page)
    assert page.evaluate("window.closesSeen") == [True]


def test_closeModal_from_descendant_dirty_guard_dismissed_keeps_open(open_modal):
    page = open_modal(enableDirtyGuard=True, dirtyMessage="Lose edits?")
    page.fill("#field", "x")

    send(page, "closeModal", selector="#field")

    assert page.dialogs == ["Lose edits?"]
    assert is_open(page)
    assert page.evaluate("window.closesSeen") == []


def test_closeModal_outside_any_modal_is_ignored(open_modal):
    page = open_modal()
    page.evaluate("document.body.insertAdjacentHTML('beforeend', '<p id=\"out\">')")

    send(page, "closeModal", selector="#out")

    assert is_open(page)
    assert page.evaluate("window.closesSeen") == [False]


NESTED = """
{% from "jinja_ui_kit/components/modal/macro.html" import modal %}
{% call modal({"id": "outer", "autoOpen": True}) %}
  {% call modal({"id": "inner", "autoOpen": True}) %}
    <button type="button" id="inside-inner">Save</button>
  {% endcall %}
{% endcall %}
"""


def test_closeModal_in_nested_modal_closes_only_innermost(render_page):
    page = render_page(NESTED)

    send(page, "closeModal", selector="#inside-inner")

    hidden = "id => document.getElementById(id).matches('.hidden')"
    assert page.evaluate(hidden, "inner") is True
    assert page.evaluate(hidden, "outer") is False


def test_closeModal_on_nested_overlay_closes_only_that_overlay(render_page):
    page = render_page(NESTED)

    send(page, "closeModal", selector="#inner")

    hidden = "id => document.getElementById(id).matches('.hidden')"
    assert page.evaluate(hidden, "inner") is True
    assert page.evaluate(hidden, "outer") is False


FORM = """
{% from "jinja_ui_kit/components/modal/macro.html" import modal %}
{% if wrap %}<div data-jui-dirty-ignore>{% endif %}
{% call modal({"id": "m", "autoOpen": True, "enableDirtyGuard": True}) %}
  <input id="text" value="t">
  <textarea id="area">a</textarea>
  <select id="sel"><option value="a">A</option><option value="b">B</option></select>
  <input type="checkbox" id="check">
  <input type="radio" name="r" id="ra" value="a" checked>
  <input type="radio" name="r" id="rb" value="b">
  <input type="search" id="search">
  <input id="halted">
  <input id="ignored" data-jui-dirty-ignore>
  <div data-jui-dirty-ignore><input id="wrapped"></div>
  <div id="editable" contenteditable>e</div>
{% endcall %}
{% if wrap %}</div>{% endif %}
"""

HALT = """() => {
  const halted = document.getElementById('halted');
  for (const type of ['input', 'change']) {
    halted.addEventListener(type, e => e.stopPropagation());
  }
}"""


@pytest.fixture
def form_modal(render_page):
    def form_modal(wrap=False):
        page = render_page(FORM, wrap=wrap)
        page.evaluate(HALT)
        record_dialogs(page)
        return page

    return form_modal


def prompts_on_close(page):
    send(page, "closeModal")
    return page.dialogs == ["Discard unsaved changes?"]


@pytest.mark.parametrize("selector", ["#halted", "#ignored", "#wrapped", "#search"])
def test_dirty_guard_ignores_exempt_controls(form_modal, selector):
    page = form_modal()

    page.fill(selector, "x")

    assert not prompts_on_close(page)
    assert not is_open(page)


EDITS = {
    "text": lambda page: page.fill("#text", "x"),
    "textarea": lambda page: page.fill("#area", "x"),
    "select": lambda page: (page.focus("#sel"), page.select_option("#sel", "b")),
    "checkbox": lambda page: page.check("#check"),
    "radio": lambda page: page.check("#rb"),
    "contenteditable": lambda page: page.fill("#editable", "x"),
}


@pytest.mark.parametrize("edit", EDITS.values(), ids=EDITS.keys())
def test_dirty_guard_prompts_after_real_edit(form_modal, edit):
    page = form_modal()

    edit(page)

    assert prompts_on_close(page)
    assert is_open(page)


REVERTS = {
    "text": lambda page: (page.fill("#text", "x"), page.fill("#text", "t")),
    "textarea": lambda page: (page.fill("#area", "x"), page.fill("#area", "a")),
    "select": lambda page: (
        page.focus("#sel"),
        page.select_option("#sel", "b"),
        page.select_option("#sel", "a"),
    ),
    "checkbox": lambda page: (page.click("#check"), page.click("#check")),
    "radio": lambda page: (page.check("#rb"), page.check("#ra")),
}


@pytest.mark.parametrize("revert", REVERTS.values(), ids=REVERTS.keys())
def test_dirty_guard_ignores_reverted_edit(form_modal, revert):
    page = form_modal()

    revert(page)

    assert not prompts_on_close(page)
    assert not is_open(page)


def test_dirty_ignore_outside_modal_does_not_exempt_it(form_modal):
    page = form_modal(wrap=True)

    page.fill("#text", "x")

    assert prompts_on_close(page)


def test_markModalClean_rebaselines_focused_control(form_modal):
    page = form_modal()
    page.fill("#text", "x")
    send(page, "markModalClean", bubbles=False)

    page.fill("#text", "y")
    page.fill("#text", "x")

    assert not prompts_on_close(page)


def test_edit_after_markModalClean_prompts(form_modal):
    page = form_modal()
    page.fill("#text", "x")
    send(page, "markModalClean", bubbles=False)

    page.fill("#text", "y")

    assert prompts_on_close(page)


def test_non_bubbling_input_event_does_not_mark_dirty(form_modal):
    page = form_modal()

    send(page, "input", bubbles=False, selector="#text")

    assert not prompts_on_close(page)


TWO_FORMS = """
{% from "jinja_ui_kit/components/modal/macro.html" import modal %}
{% call modal({"id": "m", "autoOpen": True, "enableDirtyGuard": True}) %}
  <form><input type="radio" name="r" id="a1" value="a" checked>
    <input type="radio" name="r" id="b1" value="b"></form>
  <form><input type="radio" name="r" id="a2" value="a">
    <input type="radio" name="r" id="b2" value="b" checked></form>
{% endcall %}
"""


def test_same_named_radio_groups_in_different_forms_keep_own_baselines(render_page):
    page = render_page(TWO_FORMS)
    record_dialogs(page)

    page.check("#b1")
    page.check("#a1")
    page.check("#a2")

    assert prompts_on_close(page)
