// Generic drag-to-reorder for a <ul> of draggable <li data-id="..."> items.
// Moving an item in the DOM also moves any hidden inputs (with a form="..."
// attribute) that live inside it, so the submitted order matches the visual
// order without any nested <form> elements.
function initSortable(listId) {
  const list = document.getElementById(listId);
  if (!list) return;
  let dragEl = null;

  list.addEventListener("dragstart", (e) => {
    dragEl = e.target.closest("li");
    e.dataTransfer.effectAllowed = "move";
  });

  list.addEventListener("dragover", (e) => {
    e.preventDefault();
    const target = e.target.closest("li");
    if (!target || target === dragEl) return;
    const rect = target.getBoundingClientRect();
    const after = (e.clientY - rect.top) > rect.height / 2;
    list.insertBefore(dragEl, after ? target.nextSibling : target);
  });
}

// Minimal rich-text toolbar for the post body editor. Uses execCommand,
// which is deprecated but simple and dependency-free for a local-only tool.
function initRichText(editorId, hiddenInputId) {
  const editor = document.getElementById(editorId);
  const hidden = document.getElementById(hiddenInputId);
  if (!editor || !hidden) return;

  document.querySelectorAll(`[data-cmd][data-target="${editorId}"]`).forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      editor.focus();
      const cmd = btn.dataset.cmd;
      if (cmd === "createLink") {
        const url = prompt("Link URL:");
        if (url) document.execCommand(cmd, false, url);
      } else {
        document.execCommand(cmd, false, null);
      }
    });
  });

  editor.closest("form").addEventListener("submit", () => {
    hidden.value = editor.innerHTML;
  });
}
