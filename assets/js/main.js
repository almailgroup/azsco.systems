/* AZSCO Security — site behaviour */
(function () {
  'use strict';

  var doc = document;
  var on = function (el, ev, fn) { if (el) el.addEventListener(ev, fn); };
  var all = function (sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); };

  /* ---------- mark the active nav item ---------- */
  // Pages live at clean directory URLs ("/about/", "/ar/services/") rather
  // than filenames, so a link is "here" by comparing normalized paths, not
  // the last path segment. A trailing slash is added only to extension-less
  // paths, so a real file (e.g. "/404.html") is left alone.
  function normalizePath(path) {
    if (!path) return path;
    if (/\.[a-z0-9]+$/i.test(path)) return path;
    return path.charAt(path.length - 1) === '/' ? path : path + '/';
  }

  function markActive() {
    var here = normalizePath(location.pathname);
    all('.nav a, .mobile-nav a').forEach(function (a) {
      var raw = (a.getAttribute('href') || '').split('#')[0];
      if (!raw) return;
      if (normalizePath(raw) !== here) return;
      var item = a.closest('li');
      if (!item) return;
      item.classList.add('is-active');
      var sub = a.closest('.subnav');
      if (sub) sub.closest('li').classList.add('is-active');
    });
  }

  /* ---------- sticky header shadow ---------- */
  function stickyHeader() {
    var header = doc.querySelector('.site-header');
    if (!header) return;
    var toggle = function () { header.classList.toggle('is-stuck', window.scrollY > 10); };
    toggle();
    on(window, 'scroll', toggle, { passive: true });
  }

  /* ---------- mobile drawer ---------- */
  function mobileNav() {
    var burger = doc.querySelector('.burger');
    var drawer = doc.querySelector('.mobile-nav');
    var backdrop = doc.querySelector('.backdrop');
    var closeBtn = doc.querySelector('.mobile-nav .close');
    if (!burger || !drawer || !backdrop) return;

    function setState(open) {
      drawer.classList.toggle('is-open', open);
      backdrop.classList.toggle('is-open', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      doc.body.style.overflow = open ? 'hidden' : '';
      if (open) { var f = drawer.querySelector('a, button'); if (f) f.focus(); }
    }

    on(burger, 'click', function () { setState(!drawer.classList.contains('is-open')); });
    on(backdrop, 'click', function () { setState(false); });
    on(closeBtn, 'click', function () { setState(false); burger.focus(); });
    all('.mobile-nav a').forEach(function (a) { on(a, 'click', function () { setState(false); }); });
    on(doc, 'keydown', function (e) {
      if (e.key === 'Escape' && drawer.classList.contains('is-open')) { setState(false); burger.focus(); }
    });
    on(window, 'resize', function () {
      if (window.innerWidth > 1100 && drawer.classList.contains('is-open')) setState(false);
    });
  }

  /* ---------- collapsible groups inside the mobile drawer ---------- */
  function mobileGroups() {
    var groups = all('.m-group');
    if (!groups.length) return;

    function setOpen(group, open) {
      var btn = group.querySelector('.m-toggle');
      group.classList.toggle('is-open', open);
      if (btn) btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }

    groups.forEach(function (group) {
      var btn = group.querySelector('.m-toggle');
      // start expanded when the group contains the page being viewed
      if (group.querySelector('.is-active, [aria-current]')) setOpen(group, true);
      on(btn, 'click', function () {
        var open = !group.classList.contains('is-open');
        // one open group at a time keeps the drawer short
        if (open) groups.forEach(function (g) { if (g !== group) setOpen(g, false); });
        setOpen(group, open);
      });
    });
  }

  /* ---------- reveal on scroll ---------- */
  function reveal() {
    var items = all('.reveal');
    if (!items.length) return;
    if (!('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var delay = parseInt(el.getAttribute('data-delay') || '0', 10);
        setTimeout(function () { el.classList.add('is-in'); }, delay);
        io.unobserve(el);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ---------- animated counters ---------- */
  function counters() {
    var nums = all('[data-count]');
    if (!nums.length) return;

    function run(el) {
      var target = parseFloat(el.getAttribute('data-count'));
      // years and other bare numbers must not get a thousands separator
      var plain = el.hasAttribute('data-plain');
      var dur = 1600;
      var start = null;
      function frame(ts) {
        if (start === null) start = ts;
        var p = Math.min((ts - start) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        var v = Math.round(target * eased);
        el.textContent = plain ? String(v) : v.toLocaleString('en-US');  // Latin digits in both languages
        if (p < 1) requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }

    if (!('IntersectionObserver' in window)) { nums.forEach(run); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        run(entry.target);
        io.unobserve(entry.target);
      });
    }, { threshold: 0.5 });
    nums.forEach(function (el) { io.observe(el); });
  }

  /* ---------- accordions ---------- */
  function accordions() {
    all('.acc').forEach(function (acc) {
      var btn = acc.querySelector('.acc-btn');
      var panel = acc.querySelector('.acc-panel');
      if (!btn || !panel) return;

      if (acc.classList.contains('is-open')) {
        btn.setAttribute('aria-expanded', 'true');
        panel.style.maxHeight = panel.scrollHeight + 'px';
      } else {
        btn.setAttribute('aria-expanded', 'false');
      }

      on(btn, 'click', function () {
        var open = acc.classList.toggle('is-open');
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        panel.style.maxHeight = open ? panel.scrollHeight + 'px' : 0;
      });
    });

    on(window, 'resize', function () {
      all('.acc.is-open .acc-panel').forEach(function (p) { p.style.maxHeight = p.scrollHeight + 'px'; });
    });
  }

  /* ---------- back to top ---------- */
  function backToTop() {
    var btn = doc.querySelector('.to-top');
    if (!btn) return;
    on(window, 'scroll', function () {
      btn.classList.toggle('is-visible', window.scrollY > 500);
    }, { passive: true });
    on(btn, 'click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }

  /* ---------- pre-fill the enquiry from a "Request a Quote" link ----------
     contact.html?service=<anchor> (sent by each service's quote button on
     the services page) selects "Inquiry About a Service" and drops the
     service's name into the message field, so the visitor lands ready to
     send that enquiry rather than a blank general one. */
  /* ---------- the quote basket ----------------------------------------
     Products the visitor has collected, kept in localStorage so the list
     survives moving between pages, and read back on the quote page. It is
     deliberately the only place basket state lives: the add buttons carry
     the product's name and kind as data-, so this file needs no copy of the
     catalogue and cannot disagree with the generated pages about what a
     product is called -- including in Arabic, where the data- values are
     already the Arabic strings.

     Every read and write is guarded: in private mode, or with site data
     blocked, localStorage throws on access rather than returning null, and
     an unguarded read would take the whole script down with it. */
  var QUOTE_KEY = 'azsco-quote';

  function basketRead() {
    try {
      var raw = window.localStorage.getItem(QUOTE_KEY);
      var list = raw ? JSON.parse(raw) : [];
      return Object.prototype.toString.call(list) === '[object Array]' ? list : [];
    } catch (e) { return []; }
  }

  function basketWrite(list) {
    try { window.localStorage.setItem(QUOTE_KEY, JSON.stringify(list)); } catch (e) { /* ignore */ }
    basketCount();
  }

  function basketCount() {
    var total = basketRead().reduce(function (n, it) { return n + (it.qty || 1); }, 0);
    all('.js-quote-count').forEach(function (el) {
      el.textContent = String(total);
      el.hidden = total === 0;
    });
    return total;
  }

  /* Add buttons, on cards and on the product page. */
  function addButtons() {
    var buttons = all('.js-add');
    if (!buttons.length) return;

    function markAdded(btn) {
      var label = btn.querySelector('.js-add-label');
      if (label) label.textContent = btn.getAttribute('data-added') || label.textContent;
      btn.classList.add('is-added');
    }

    // Reflect what is already in the basket, so returning to a page does not
    // invite the visitor to add the same item twice.
    var inBasket = {};
    basketRead().forEach(function (it) { inBasket[it.sku] = true; });
    buttons.forEach(function (btn) {
      if (inBasket[btn.getAttribute('data-sku')]) markAdded(btn);
    });

    buttons.forEach(function (btn) {
      on(btn, 'click', function () {
        var sku = btn.getAttribute('data-sku');
        if (!sku) return;
        var list = basketRead();
        var found = null;
        list.forEach(function (it) { if (it.sku === sku) found = it; });
        if (found) found.qty = (found.qty || 1) + 1;
        else list.push({
          sku: sku,
          name: btn.getAttribute('data-name') || sku,
          kind: btn.getAttribute('data-kind') || '',
          cat: btn.getAttribute('data-cat') || '',
          qty: 1
        });
        basketWrite(list);
        markAdded(btn);
      });
    });
  }

  /* ---------- the quote page's list ---------- */
  function quoteList() {
    var list = doc.querySelector('.js-quote-list');
    if (!list) return;
    var empty = doc.querySelector('.js-quote-empty');
    var form = doc.querySelector('#quote-form');
    var clear = doc.querySelector('.js-clear-quote');
    var labels = list.getAttribute('data-labels');
    try { labels = JSON.parse(labels || '{}'); } catch (e) { labels = {}; }

    function render() {
      var items = basketRead();
      list.textContent = '';
      list.hidden = items.length === 0;
      if (empty) empty.hidden = items.length > 0;
      if (form) form.hidden = false;
      if (clear) clear.hidden = items.length === 0;

      items.forEach(function (it, index) {
        var li = doc.createElement('li');
        li.className = 'q-item';

        var text = doc.createElement('div');
        text.className = 'q-item-text';
        var b = doc.createElement('b');
        // textContent, not innerHTML: the basket is editable by anyone with
        // devtools, so nothing from it is ever parsed as markup.
        b.textContent = it.name || it.sku;
        var small = doc.createElement('small');
        small.textContent = [it.cat, it.kind].filter(Boolean).join(' · ');
        text.appendChild(b);
        text.appendChild(small);

        var qty = doc.createElement('div');
        qty.className = 'q-qty';
        var minus = doc.createElement('button');
        minus.type = 'button';
        minus.textContent = '−';
        minus.setAttribute('aria-label', labels.less || 'Decrease quantity');
        var input = doc.createElement('input');
        input.type = 'number';
        input.min = '1';
        input.value = String(it.qty || 1);
        input.setAttribute('aria-label', labels.qty || 'Quantity');
        var plus = doc.createElement('button');
        plus.type = 'button';
        plus.textContent = '+';
        plus.setAttribute('aria-label', labels.more || 'Increase quantity');
        qty.appendChild(minus);
        qty.appendChild(input);
        qty.appendChild(plus);

        var remove = doc.createElement('button');
        remove.type = 'button';
        remove.className = 'q-remove';
        remove.setAttribute('aria-label', (labels.remove || 'Remove') + ': ' + (it.name || it.sku));
        remove.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"'
          + ' stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>';

        function setQty(n) {
          var items2 = basketRead();
          if (!items2[index]) return;
          if (n < 1) items2.splice(index, 1);
          else items2[index].qty = n;
          basketWrite(items2);
          render();
        }
        on(minus, 'click', function () { setQty((parseInt(input.value, 10) || 1) - 1); });
        on(plus, 'click', function () { setQty((parseInt(input.value, 10) || 1) + 1); });
        on(input, 'change', function () { setQty(parseInt(input.value, 10) || 1); });
        on(remove, 'click', function () { setQty(0); });

        li.appendChild(text);
        li.appendChild(qty);
        li.appendChild(remove);
        list.appendChild(li);
      });
    }

    all('.js-clear-quote').forEach(function (btn) {
      on(btn, 'click', function () { basketWrite([]); render(); });
    });
    render();
  }

  /* ---------- catalogue filters ----------------------------------------
     Filtering happens in the browser against data- attributes the builder
     wrote onto each card, so there is no second copy of the catalogue in
     JavaScript and no request to make. With scripting off, every card is
     simply visible -- which is the correct catalogue, just unfiltered. */
  function catalogueFilters() {
    var form = doc.querySelector('#filters');
    var results = doc.querySelector('.js-results');
    if (!form || !results) return;
    var cards = all('.p-card', results);
    var count = doc.querySelector('.js-count');
    var empty = doc.querySelector('.js-empty');

    function checked(name) {
      return all('input[name="' + name + '"]:checked', form)
        .map(function (i) { return i.value; });
    }

    function apply() {
      var cats = checked('cat');
      var brands = checked('brand');
      var shown = 0;

      cards.forEach(function (card) {
        var cat = card.getAttribute('data-cat') || '';
        var cardBrands = (card.getAttribute('data-brands') || '').split(' ');
        var catOk = !cats.length || cats.indexOf(cat) !== -1;
        var brandOk = !brands.length || brands.some(function (b) {
          return cardBrands.indexOf(b) !== -1;
        });
        var show = catOk && brandOk;
        card.hidden = !show;
        if (show) shown++;
      });

      if (count) count.textContent = String(shown);
      if (empty) empty.hidden = shown > 0;
      results.hidden = shown === 0;
    }

    on(form, 'change', apply);
    all('.js-clear').forEach(function (btn) {
      on(btn, 'click', function () {
        all('input[type="checkbox"]', form).forEach(function (i) { i.checked = false; });
        apply();
      });
    });
    apply();
  }

  /* ---------- quote form ----------------------------------------------
     Validates, attaches the basket, and posts to the same worker route the
     contact form uses. It never reports success it did not get: with no
     endpoint configured, or on a failed request, it says so and gives the
     phone number instead. */
  function quoteForm() {
    var form = doc.querySelector('#quote-form');
    if (!form) return;
    var msg = form.querySelector('.form-msg');
    var submit = form.querySelector('[type="submit"]');
    var itemsField = form.querySelector('.js-quote-items');

    function fields() {
      return all('input, select, textarea', form).filter(function (f) {
        return f.name && f.name !== 'website' && f.type !== 'hidden';
      });
    }

    function setError(field, on_) {
      var wrap = field.closest('.field');
      if (wrap) wrap.classList.toggle('is-invalid', on_);
    }

    function check(field) {
      var value = (field.value || '').trim();
      var ok = true;
      if (field.hasAttribute('required') && !value) ok = false;
      if (ok && field.type === 'email' && value) ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value);
      setError(field, !ok);
      return ok;
    }

    fields().forEach(function (f) {
      on(f, 'blur', function () { check(f); });
      on(f, 'input', function () { if (f.closest('.field').classList.contains('is-invalid')) check(f); });
    });

    function say(text) { if (msg) msg.textContent = text || ''; }

    on(form, 'submit', function (e) {
      e.preventDefault();
      var ok = true;
      fields().forEach(function (f) { if (!check(f)) ok = false; });
      if (!ok) {
        var first = form.querySelector('.is-invalid input, .is-invalid select, .is-invalid textarea');
        if (first) first.focus();
        return;
      }

      // The basket travels as a readable list, so the enquiry email says what
      // was asked for without anyone having to decode JSON.
      var items = basketRead();
      var summary = items.map(function (it) {
        return (it.qty || 1) + ' × ' + (it.name || it.sku)
          + (it.cat ? ' (' + it.cat + ')' : '');
      }).join('\n');
      if (itemsField) itemsField.value = summary;

      var endpoint = form.getAttribute('data-endpoint');
      var payload = { lang: form.getAttribute('data-lang') || 'en' };
      fields().forEach(function (f) {
        payload[f.name] = (f.tagName === 'SELECT' && f.selectedIndex >= 0)
          ? f.options[f.selectedIndex].text
          : f.value;
      });
      payload.items = summary;
      // Fold the basket into the message too: the worker relays a fixed set
      // of fields, and the enquiry is useless without the list.
      if (summary) payload.message = (payload.message || '') + '\n\n--\n' + summary;
      var honeypot = form.querySelector('[name="website"]');
      if (honeypot) payload.website = honeypot.value;

      if (!endpoint) { say(form.getAttribute('data-failed')); return; }

      if (submit) submit.disabled = true;
      say(form.getAttribute('data-sending'));

      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function (res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          return res.json();
        })
        .then(function () {
          say(form.getAttribute('data-sent'));
          form.reset();
          basketWrite([]);
          var list = doc.querySelector('.js-quote-list');
          if (list) { list.textContent = ''; list.hidden = true; }
          var empty = doc.querySelector('.js-quote-empty');
          if (empty) empty.hidden = false;
          all('.js-clear-quote').forEach(function (b) { b.hidden = true; });
        })
        .catch(function () { say(form.getAttribute('data-failed')); })
        .then(function () { if (submit) submit.disabled = false; });
    });
  }

  /* ---------- keep "years of experience" current without a rebuild ---------- */
  function yearsSince() {
    all('[data-years-since]').forEach(function (el) {
      var from = parseInt(el.getAttribute('data-years-since'), 10);
      if (!from) return;
      var n = new Date().getFullYear() - from;
      if (n < 0) return;
      // the counter animation reads data-count, so update that too
      el.setAttribute('data-count', String(n));
      el.textContent = String(n);
    });
  }

  /* ---------- current year in footer ---------- */
  function year() {
    all('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
  }

  function init() {
    markActive();
    stickyHeader();
    mobileNav();
    mobileGroups();
    reveal();
    yearsSince();   // must run before counters() so it animates to the right figure
    counters();
    accordions();
    backToTop();
    basketCount();  // the badge reflects storage on load, not only after a write
    addButtons();
    quoteList();
    catalogueFilters();
    quoteForm();
    year();
  }

  if (doc.readyState === 'loading') on(doc, 'DOMContentLoaded', init);
  else init();
})();
