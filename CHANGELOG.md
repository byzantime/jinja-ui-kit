# Changelog

## 0.3.2

- Fix: on mobile browsers, modals (especially `size: 'fullscreen'`) no longer grow taller than the visible screen while the address bar is showing, which pushed the header and footer off-screen. Panel heights now use `dvh`, with a `vh` fallback for browsers without `dvh` support.
- Modal dirty guard (`enableDirtyGuard`) now compares values: a modal is dirty only while an edited control differs from its value when first focused since the modal opened or was last marked clean, so reverting an edit no longer prompts.
- Modal dirty guard listens for `input`/`change` in the bubble phase, so a control that stops its events propagating (e.g. an auto-saving one using hyperscript's `halt bubbling`) no longer marks the modal dirty. Non-bubbling synthetic `input`/`change` events no longer mark it dirty either.
- New `data-jui-dirty-ignore` attribute: edits to a control carrying it, or inside an element in the modal carrying it, never mark the modal dirty.
- Search inputs (`type="search"`) are ignored by the dirty guard.

## 0.3.1

- Fix: a `closeModal` event dispatched on any element inside a modal (e.g. a form whose htmx response sets `HX-Trigger: closeModal`) closes the innermost enclosing modal again, as it did in 0.2.0. In 0.3.0 only an event targeting the overlay itself did.

## 0.3.0

- Modal and button behaviour moved from hyperscript to the kit's delegated JS; see "Upgrading to 0.3" in the README.
