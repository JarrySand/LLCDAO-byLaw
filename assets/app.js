/* global marked, hljs */
(function () {
  const state = {
    docs: (window.DOCS || []),
    byId: new Map(),
  };

  function createEl(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text) el.textContent = text;
    return el;
  }

  function buildIndex() {
    const nav = document.getElementById('nav');
    nav.innerHTML = '';
    state.byId.clear();

    for (const section of state.docs) {
      const secEl = createEl('div', 'section');
      const header = createEl('div', 'section-header');
      const caret = createEl('span', 'caret');
      const title = createEl('span', null, section.title);
      header.appendChild(caret);
      header.appendChild(title);
      header.addEventListener('click', () => {
        const collapsed = secEl.classList.toggle('collapsed');
        try { localStorage.setItem(`section:${section.key || section.title}`, collapsed ? '1' : '0'); } catch (_) {}
      });
      secEl.appendChild(header);

      const content = createEl('div', 'section-content');
      for (const doc of section.items) {
        state.byId.set(doc.id, doc);
        const a = createEl('a', 'link');
        a.href = `#${encodeURIComponent(doc.id)}`;
        a.textContent = doc.title;
        a.dataset.docId = doc.id;
        content.appendChild(a);
      }
      secEl.appendChild(content);

      // restore collapsed state
      try {
        const saved = localStorage.getItem(`section:${section.key || section.title}`);
        if (saved === '1') secEl.classList.add('collapsed');
      } catch (_) {}

      nav.appendChild(secEl);
    }
  }

  function setActiveLink(docId) {
    document.querySelectorAll('.link').forEach((el) => {
      el.classList.toggle('active', el.dataset.docId === docId);
    });
  }

  async function renderDoc(doc) {
    const container = document.getElementById('content');
    container.innerHTML = '<p>読み込み中...</p>';
    try {
      const res = await fetch(encodeURI(doc.path), { cache: 'no-cache' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const md = await res.text();
      const html = marked.parse(md, { mangle: false, headerIds: true });
      container.innerHTML = html;
      // Highlight code blocks if present
      document.querySelectorAll('pre code').forEach((block) => {
        try { hljs.highlightElement(block); } catch (_) {}
      });
      document.title = `${doc.title} — LLCDAO`;
    } catch (err) {
      container.innerHTML = `<p>読み込みに失敗しました: ${String(err)}</p>`;
    }
  }

  function onHashChange() {
    const raw = (location.hash || '#').slice(1);
    const docId = decodeURIComponent(raw);
    const doc = state.byId.get(docId);
    if (doc) {
      setActiveLink(docId);
      renderDoc(doc);
    }
  }

  // init
  buildIndex();
  window.addEventListener('hashchange', onHashChange);
  // Load first item if no hash
  if (!location.hash) {
    const first = state.docs[0]?.items?.[0];
    if (first) location.hash = `#${encodeURIComponent(first.id)}`;
  } else {
    onHashChange();
  }
})();


