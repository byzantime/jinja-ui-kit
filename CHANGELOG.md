# Changelog

## 0.3.1

- Fix: a `closeModal` event dispatched on any element inside a modal (e.g. a form whose htmx response sets `HX-Trigger: closeModal`) closes the innermost enclosing modal again, as it did in 0.2.0. In 0.3.0 only an event targeting the overlay itself did.

## 0.3.0

- Modal and button behaviour moved from hyperscript to the kit's delegated JS; see "Upgrading to 0.3" in the README.
