/* AZSCO Assistant — chat widget.
 *
 * Posts {lang, messages} to the proxy named in data-endpoint (set by
 * tools/build.py from CHAT_ENDPOINT) and renders the {reply} that comes back.
 * The proxy — backend/workers/chat-worker.js, or backend/api/chat.js on a Node
 * host — holds the model API key and builds the system prompt, so neither ever
 * reaches the browser.
 *
 * Calling a model API straight from the page was tried and dropped: providers
 * reject browser-origin requests, and the key would be readable in the source.
 *
 * Every visible string is authored per language in the markup, so this file
 * contains no copy of its own.
 */
(function () {
  'use strict';

  var root = document.querySelector('[data-azsco-chat]');
  if (!root) return;

  var launcher = root.querySelector('.chat-launcher');
  var panel    = root.querySelector('.chat-panel');
  var log      = root.querySelector('.chat-log');
  var form     = root.querySelector('.chat-form');
  var input    = root.querySelector('.chat-form textarea');
  var send     = root.querySelector('.chat-send');
  var suggest  = root.querySelector('.chat-suggest');
  var btnClose = root.querySelector('[data-chat-close]');
  var btnExpand= root.querySelector('[data-chat-expand]');

  var endpoint = root.getAttribute('data-endpoint') || '';
  var lang     = root.getAttribute('data-lang') || 'en';
  var greeting = root.getAttribute('data-greeting') || '';
  var errText  = root.getAttribute('data-error') || '';
  var offline  = root.getAttribute('data-offline') || '';
  var labelExpand   = root.getAttribute('data-label-expand') || '';
  var labelCollapse = root.getAttribute('data-label-collapse') || '';

  var STORE = 'azsco-chat-' + lang;
  var MAX_CHARS = 1000;      // matches the proxy's limit
  var MAX_TURNS = 20;        // how much history we send back

  var history = [];          // [{role:'user'|'assistant', content:'...'}]
  var busy = false;

  /* ---------- helpers ---------- */
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  // Model output is escaped first, then a small, closed set of formatting is
  // re-introduced. Nothing from the model reaches the DOM as live markup.
  function render(text) {
    var html = esc(text);
    html = html.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');
    // Kuwaiti numbers are usually written "(+965) 1808606", so allow a leading bracket
    html = html.replace(/(^|\s)(\(?\+?\d[\d\s()-]{6,}\d)/g, function (m, pre, num) {
      return pre + '<a href="tel:' + num.replace(/[^\d+]/g, '') + '">' + num + '</a>';
    });
    html = html.replace(/([\w.+-]+@[\w-]+\.[\w.]+)/g, '<a href="mailto:$1">$1</a>');
    return html.split(/\n{2,}/).map(function (p) {
      return '<p>' + p.replace(/\n/g, '<br>') + '</p>';
    }).join('');
  }

  function addMsg(role, text, isError) {
    var el = document.createElement('div');
    el.className = 'chat-msg from-' + role + (isError ? ' is-error' : '');
    el.innerHTML = render(text);
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }

  function typing(on) {
    var existing = log.querySelector('.chat-typing');
    if (!on) { if (existing) existing.remove(); return; }
    if (existing) return;
    var el = document.createElement('div');
    el.className = 'chat-typing';
    el.setAttribute('aria-label', '…');
    el.innerHTML = '<span></span><span></span><span></span>';
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
  }

  function save() {
    try { sessionStorage.setItem(STORE, JSON.stringify(history.slice(-MAX_TURNS * 2))); }
    catch (e) { /* private mode, or storage disabled */ }
  }

  function restore() {
    var raw = null;
    try { raw = sessionStorage.getItem(STORE); } catch (e) { return false; }
    if (!raw) return false;
    try {
      var saved = JSON.parse(raw);
      if (!Array.isArray(saved) || !saved.length) return false;
      saved.forEach(function (m) {
        history.push(m);
        addMsg(m.role === 'user' ? 'user' : 'bot', m.content);
      });
      return true;
    } catch (e) { return false; }
  }

  /* ---------- open / close / expand ---------- */
  var lastFocus = null;

  function open() {
    lastFocus = document.activeElement;
    panel.classList.add('is-open');
    panel.removeAttribute('hidden');
    launcher.setAttribute('aria-expanded', 'true');
    if (!log.children.length) {
      if (!restore() && greeting) addMsg('bot', greeting);
    }
    setTimeout(function () { input.focus(); }, 60);
  }

  function close() {
    panel.classList.remove('is-open');
    launcher.setAttribute('aria-expanded', 'false');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function toggleExpand() {
    var big = panel.classList.toggle('is-expanded');
    btnExpand.setAttribute('aria-label', big ? labelCollapse : labelExpand);
    btnExpand.setAttribute('aria-pressed', big ? 'true' : 'false');
    input.focus();
  }

  launcher.addEventListener('click', function () {
    panel.classList.contains('is-open') ? close() : open();
  });
  btnClose.addEventListener('click', close);
  btnExpand.addEventListener('click', toggleExpand);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && panel.classList.contains('is-open')) close();
  });

  /* ---------- sending ---------- */
  function setBusy(on) {
    busy = on;
    send.disabled = on;
    input.disabled = on;
  }

  function ask(text) {
    text = String(text || '').trim().slice(0, MAX_CHARS);
    if (!text || busy) return;

    if (suggest) suggest.hidden = true;
    addMsg('user', text);
    history.push({ role: 'user', content: text });
    input.value = '';
    input.style.height = '';
    setBusy(true);
    typing(true);

    if (!endpoint) {
      typing(false);
      setBusy(false);
      addMsg('bot', offline, true);
      return;
    }

    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lang: lang, messages: history.slice(-MAX_TURNS * 2) })
    })
      .then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      })
      .then(function (data) {
        var reply = data && data.reply && String(data.reply).trim();
        if (!reply) throw new Error('empty reply');
        typing(false);
        addMsg('bot', reply);
        history.push({ role: 'assistant', content: reply });
        save();
      })
      .catch(function () {
        typing(false);
        // The visitor should always be left with a way to reach a human.
        addMsg('bot', errText, true);
      })
      .then(function () { setBusy(false); input.focus(); });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    ask(input.value);
  });

  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(input.value); }
  });

  input.addEventListener('input', function () {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  });

  if (suggest) {
    suggest.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (b) ask(b.textContent.trim());
    });
  }
})();
