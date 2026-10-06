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
  // Dirty-guard state, keyed by overlay.
  const dirty = new WeakMap();
  // Content panels that already swallow clicks.
  const swallowing = new WeakSet();

  function isModal(el) {
    return el instanceof Element && el.matches(MODAL);
  }

  function sendCloseModal(modal) {
    modal.dispatchEvent(new CustomEvent("closeModal", { bubbles: true }));
  }

  function swallowClick(e) {
    e.stopPropagation();
  }

  function markDirty(modal) {
    if (dirty.has(modal)) return;
    // Any class change (closing, or reopening) resets the flag, so a
    // reopened modal starts clean.
    const observer = new MutationObserver(function () {
      clearDirty(modal);
    });
    observer.observe(modal, { attributes: true, attributeFilter: ["class"] });
    dirty.set(modal, observer);
  }

  function clearDirty(modal) {
    const observer = dirty.get(modal);
    if (!observer) return;
    observer.disconnect();
    dirty.delete(modal);
  }

  document.addEventListener(
    "mousedown",
    function (e) {
      const modal = e.target instanceof Element && e.target.closest(MODAL);
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
      const modal =
        e.target instanceof Element ? e.target.closest(MODAL) : null;
      if (!modal || modal.classList.contains("hidden")) return;
      if (
        modal.hasAttribute("data-jui-dirty-guard") &&
        dirty.has(modal) &&
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

  function onEdit(e) {
    const modal =
      e.target instanceof Element &&
      e.target.closest(MODAL + "[data-jui-dirty-guard]");
    if (modal && !modal.classList.contains("hidden")) markDirty(modal);
  }
  document.addEventListener("input", onEdit, true);
  document.addEventListener("change", onEdit, true);

  document.addEventListener(
    "markModalClean",
    function (e) {
      if (isModal(e.target)) clearDirty(e.target);
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
