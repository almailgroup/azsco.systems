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
  function prefillServiceQuery(form) {
    var match = /[?&]service=([^&]+)/.exec(location.search);
    if (!match) return;
    var anchor = decodeURIComponent(match[1]);
    var names = {};
    try { names = JSON.parse(form.getAttribute('data-service-names') || '{}'); } catch (e) { return; }
    var name = names[anchor];
    if (!name) return;

    var select = form.querySelector('#service');
    if (select) select.value = 'service';

    var message = form.querySelector('#message');
    var template = form.getAttribute('data-quote-prefill') || '';
    if (message && !message.value && template) {
      message.value = template.replace('{SERVICE}', name);
    }
  }

  /* ---------- contact form validation ---------- */
  function contactForm() {
    var form = doc.querySelector('[data-contact-form]');
    if (!form) return;
    prefillServiceQuery(form);
    var status = form.querySelector('.form-status');

    // The markup already carries each field's message, authored per language;
    // reusing it keeps the Arabic form speaking Arabic when a check fails.
    function fail(field) {
      var wrap = field.closest('.field');
      if (wrap) wrap.classList.add('has-error');
      return false;
    }

    function check(field) {
      var wrap = field.closest('.field');
      if (!wrap) return true;           // honeypot and other unwrapped inputs
      wrap.classList.remove('has-error');
      var val = (field.value || '').trim();

      if (field.hasAttribute('required') && !val) return fail(field);
      if (field.type === 'email' && val && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(val)) {
        return fail(field);
      }
      if (field.type === 'tel' && val && !/^[0-9+()\-\s]{6,}$/.test(val)) {
        return fail(field);
      }
      return true;
    }

    function fields() {
      return all('input, select, textarea', form).filter(function (f) {
        return f.name !== 'website';    // the honeypot is never validated
      });
    }

    fields().forEach(function (f) {
      on(f, 'blur', function () { check(f); });
      on(f, 'input', function () {
        var wrap = f.closest('.field');
        if (wrap && wrap.classList.contains('has-error')) check(f);
      });
    });

    // Every message is authored per language on the form element itself.
    function say(msg, isError) {
      if (!status) return;
      status.textContent = msg || '';
      status.classList.add('is-visible');
      status.classList.toggle('is-error', !!isError);
    }

    // Guarded: a form built without a .form-status element would otherwise
    // throw here and take the whole submit handler down with it.
    function scrollToStatus() {
      if (status) status.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    on(form, 'submit', function (e) {
      e.preventDefault();
      var ok = true;
      fields().forEach(function (f) { if (!check(f)) ok = false; });

      if (!ok) {
        var first = form.querySelector('.has-error input, .has-error select, .has-error textarea');
        if (first) first.focus();
        return;
      }

      var endpoint = form.getAttribute('data-endpoint');
      var submit = form.querySelector('[type="submit"]');
      var payload = { lang: form.getAttribute('data-lang') || 'en' };
      fields().forEach(function (f) {
        if (!f.name) return;
        // Send a select's visible label, not its value — the email should read
        // "Inquiry About a Service", not "service" (and in Arabic on /ar/).
        payload[f.name] = (f.tagName === 'SELECT' && f.selectedIndex >= 0)
          ? f.options[f.selectedIndex].text
          : f.value;
      });
      var honeypot = form.querySelector('[name="website"]');
      if (honeypot) payload.website = honeypot.value;

      if (!endpoint) {                      // nothing to post to — say so, don't pretend
        say(form.getAttribute('data-error-message'), true);
        scrollToStatus();
        return;
      }

      if (submit) submit.disabled = true;
      say(form.getAttribute('data-sending-message'));

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
          say(form.getAttribute('data-sent-message'));
          form.reset();
        })
        .catch(function () {
          say(form.getAttribute('data-error-message'), true);
        })
        .then(function () {
          if (submit) submit.disabled = false;
          scrollToStatus();
        });
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
    contactForm();
    year();
  }

  if (doc.readyState === 'loading') on(doc, 'DOMContentLoaded', init);
  else init();
})();
