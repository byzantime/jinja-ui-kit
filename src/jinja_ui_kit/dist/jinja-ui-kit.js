/*
 * jinja-ui-kit behaviour for the modal and button macros.
 *
 * Every listener is delegated from `document`, so markup swapped in later
 * (htmx, innerHTML, ...) needs no per-element processing. Safe to include
 * more than once, and safe to load with `<script defer>` in <head>.
 */
(function () {
  "use strict";

  if (window.__juiKit) return;
  window.__juiKit = true;

  const MODAL = "[data-jui-modal]";

  // ---------------------------------------------------------------- Modal

  // Whether the last mousedown on each modal started on its backdrop.
  const pressedBackdrop = new WeakMap();
  // Dirty-guard state, keyed by overlay: `baseline` maps each control's key
  // to its value when first seen, `edited` holds controls that have fired
  // input/change since, and `observer` resets it all on a class change.
  const guard = new WeakMap();
  // Content panels that already swallow clicks.
  const swallowing = new WeakSet();

  function isModal(el) {
    return el instanceof Element && el.matches(MODAL);
  }

  // Nearest ancestor-or-self of `el` matching `selector`, or null if `el`
  // isn't an Element (e.g. a text node, or absent).
  function closestMatch(el, selector) {
    return el instanceof Element ? el.closest(selector) : null;
  }

  function sendCloseModal(modal) {
    modal.dispatchEvent(new CustomEvent("closeModal", { bubbles: true }));
  }

  function swallowClick(e) {
    e.stopPropagation();
  }

  function guardState(modal) {
    let state = guard.get(modal);
    if (state) return state;
    // Any class change (closing, or reopening) resets the state, so a
    // reopened modal starts clean.
    const observer = new MutationObserver(function () {
      clearDirty(modal);
    });
    observer.observe(modal, { attributes: true, attributeFilter: ["class"] });
    state = { baseline: new Map(), edited: new Set(), observer };
    guard.set(modal, state);
    return state;
  }

  function clearDirty(modal) {
    const state = guard.get(modal);
    if (!state) return;
    state.observer.disconnect();
    guard.delete(modal);
  }

  // The open, guarded modal whose edits `el` counts towards, or null if
  // `el` is a search box or sits under a `[data-jui-dirty-ignore]` in it.
  function trackingModal(el) {
    const modal = closestMatch(el, MODAL + "[data-jui-dirty-guard]");
    if (!modal || modal.classList.contains("hidden")) return null;
    if (el instanceof HTMLInputElement && el.type === "search") return null;
    const ignored = el.closest("[data-jui-dirty-ignore]");
    return ignored && modal.contains(ignored) ? null : modal;
  }

  // Whether `el` has a value `readValue` can compare.
  function isComparable(el) {
    return (
      (el instanceof HTMLInputElement && el.type !== "file") ||
      el instanceof HTMLSelectElement ||
      el instanceof HTMLTextAreaElement
    );
  }

  function isNamedRadio(el) {
    return (
      el instanceof HTMLInputElement && el.type === "radio" && Boolean(el.name)
    );
  }

  // A radio group shares one baseline, so A -> B -> A reads as unchanged.
  function baselineKey(el) {
    return isNamedRadio(el) ? "radio:" + el.name : el;
  }

  function readValue(el, modal) {
    if (el.type === "checkbox") return el.checked;
    if (el.type === "radio") {
      if (!isNamedRadio(el)) return el.checked ? el.value : null;
      const scope = el.form || modal;
      const checked = Array.prototype.find.call(
        scope.querySelectorAll('input[type="radio"]'),
        function (r) {
          return r.name === el.name && r.form === el.form && r.checked;
        },
      );
      return checked ? checked.value : null;
    }
    if (el instanceof HTMLSelectElement && el.multiple) {
      return JSON.stringify(
        Array.prototype.map.call(el.selectedOptions, function (o) {
          return o.value;
        }),
      );
    }
    return el.value;
  }

  // Snapshot a control's value the first time it is focused or pressed
  // after the modal opens (or is marked clean), before the user edits it.
  function recordBaseline(el) {
    if (!isComparable(el)) return;
    const modal = trackingModal(el);
    if (!modal) return;
    const baseline = guardState(modal).baseline;
    const key = baselineKey(el);
    if (!baseline.has(key)) baseline.set(key, readValue(el, modal));
  }

  // An edit counts unless its control is back at its baseline. Controls
  // with no comparable value, no baseline (an event dispatched by script
  // without a prior focus), or swapped out since the edit are assumed dirty.
  function isDirty(modal) {
    const state = guard.get(modal);
    if (!state) return false;
    for (const el of state.edited) {
      if (!el.isConnected || !isComparable(el)) return true;
      const key = baselineKey(el);
      if (!state.baseline.has(key)) return true;
      if (readValue(el, modal) !== state.baseline.get(key)) return true;
    }
    return false;
  }

  document.addEventListener(
    "mousedown",
    function (e) {
      const modal = closestMatch(e.target, MODAL);
      if (modal) pressedBackdrop.set(modal, e.target === modal);
    },
    true,
  );

  document.addEventListener(
    "click",
    function (e) {
      if (!(e.target instanceof Element)) return;

      // Only a click whose mousedown also landed on the backdrop closes it,
      // so a drag from the content that ends outside does not.
      if (isModal(e.target)) {
        if (pressedBackdrop.get(e.target)) sendCloseModal(e.target);
        return;
      }

      const closer = e.target.closest("[data-jui-modal-close]");
      const modal = closer && closer.closest(MODAL);
      if (modal) sendCloseModal(modal);

      // Bound lazily on the content panel itself (a listener added to a node
      // the event has not reached yet still runs for this event), so clicks
      // reach their targets but stop bubbling past the panel.
      const content = e.target.closest("[data-jui-modal-content]");
      if (content && !swallowing.has(content)) {
        swallowing.add(content);
        content.addEventListener("click", swallowClick);
      }
    },
    true,
  );

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    document
      .querySelectorAll(MODAL + "[data-jui-keyboard-close]:not(.hidden)")
      .forEach(sendCloseModal);
  });

  // Capture phase: runs before any listener on the modal or its ancestors
  // (e.g. `on closeModal from body`), so a cancelled close never reaches
  // them, and a close they observe has already happened.
  //
  // The event may target the overlay or anything inside it (htmx's
  // `HX-Trigger: closeModal` fires on the element that made the request,
  // typically a form in the modal); the innermost enclosing modal closes.
  document.addEventListener(
    "closeModal",
    function (e) {
      const modal = closestMatch(e.target, MODAL);
      if (!modal || modal.classList.contains("hidden")) return;
      if (
        modal.hasAttribute("data-jui-dirty-guard") &&
        isDirty(modal) &&
        !window.confirm(modal.dataset.dirtyMessage)
      ) {
        e.preventDefault();
        e.stopImmediatePropagation();
        return;
      }
      modal.classList.add("hidden");
      modal.classList.remove("flex");
      clearDirty(modal);
    },
    true,
  );

  // Capture phase, so the snapshot precedes any edit. `pointerdown` covers
  // browsers (Safari) that don't focus checkboxes and radios on click; a
  // press on a label snapshots the control it toggles.
  function onApproach(e) {
    if (!(e.target instanceof Element)) return;
    recordBaseline(e.target);
    const label = e.target.closest("label");
    if (label && label.control) recordBaseline(label.control);
  }
  document.addEventListener("focusin", onApproach, true);
  document.addEventListener("pointerdown", onApproach, true);

  // Bubble phase, so a control that stops its input/change from
  // propagating (e.g. an auto-saving one) never marks the modal dirty.
  function onEdit(e) {
    if (!(e.target instanceof Element)) return;
    const modal = trackingModal(e.target);
    if (modal) guardState(modal).edited.add(e.target);
  }
  document.addEventListener("input", onEdit);
  document.addEventListener("change", onEdit);

  // Re-snapshot the focused control at once: it won't fire `focusin`
  // again before the user's next edit.
  document.addEventListener(
    "markModalClean",
    function (e) {
      if (!isModal(e.target)) return;
      clearDirty(e.target);
      const active = document.activeElement;
      if (active && e.target.contains(active)) recordBaseline(active);
    },
    true,
  );

  // --------------------------------------------------------------- Button

  const GUARDED =
    "button[data-prevent-double-click], input[data-prevent-double-click]";

  // A repeat click while the form is submitting is swallowed entirely.
  document.addEventListener(
    "click",
    function (e) {
      const button = e.target instanceof Element && e.target.closest(GUARDED);
      if (
        button &&
        button.form &&
        button.form.classList.contains("is-submitting")
      ) {
        e.preventDefault();
        e.stopImmediatePropagation();
      }
    },
    true,
  );

  document.addEventListener(
    "submit",
    function (e) {
      const form = e.target;
      const buttons = Array.prototype.filter.call(form.elements, function (el) {
        return el.matches(GUARDED);
      });
      if (!buttons.length) return;

      form.classList.add("is-submitting");
      // Disable after the submit has been handled, so the submitter's
      // name/value is still sent with the form.
      setTimeout(function () {
        buttons.forEach(function (b) {
          b.disabled = true;
        });
        form.addEventListener(
          "htmx:after:request",
          function () {
            buttons.forEach(function (b) {
              b.disabled = false;
            });
            form.classList.remove("is-submitting");
          },
          { once: true },
        );
      }, 0);
    },
    true,
  );
})();
