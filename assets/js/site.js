/* ==========================================================================
   pinakibhaskar.github.io — progressive enhancements (vanilla JS, no deps)

   Everything on the page works without this file. It adds:
     1. Theme toggle (persists in localStorage, sets data-theme on <html>)
     2. Mobile navigation panel; header controls kept in reading order
     3. Scroll flags: the top-bar name and the rail's buttons appear once the
        masthead / the hero buttons have scrolled away
     4. Active-section highlighting in the index (aria-current)
     5. Publications: clipped list + "Show all", type / topic / text filters
        (search ignores accents), live count, empty state
     6. "Copy address" button
     7. Lightbox for photographs and award certificates (<dialog>; without it each link opens its JPEG)
     8. Subtle reveal-on-scroll (skipped for reduced motion)

   Each block checks that its elements exist, so removing a section from
   index.html never causes an error here.
   ========================================================================== */
(function () {
  'use strict';

  var doc = document;
  var root = doc.documentElement;

  function $(sel, ctx) { return (ctx || doc).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); }
  function mq(query) { return window.matchMedia ? window.matchMedia(query) : { matches: false }; }

  /* 1. THEME ------------------------ */
  (function theme() {
    var btn = $('[data-theme-toggle]');
    if (!btn) { return; }
    var label = $('[data-theme-label]', btn);

    function current() {
      var set = root.getAttribute('data-theme');
      if (set === 'light' || set === 'dark') { return set; }
      return mq('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    function describe() {
      var next = current() === 'dark' ? 'light' : 'dark';
      btn.setAttribute('aria-label', 'Switch to ' + next + ' theme');
      if (label) { label.textContent = next === 'dark' ? 'Dark theme' : 'Light theme'; }
    }
    // A manual choice overrides the media-specific theme-color metas (browser chrome colour).
    // The colour is read from the --paper token, so site.css stays the only place it is defined.
    function syncThemeColor() {
      if (!root.hasAttribute('data-theme')) { return; }
      var paper = getComputedStyle(root).getPropertyValue('--paper').trim();
      if (paper) { $$('meta[name="theme-color"]').forEach(function (m) { m.setAttribute('content', paper); }); }
    }
    function apply(theme) {
      root.setAttribute('data-theme', theme);
      try { localStorage.setItem('theme', theme); } catch (e) { /* private mode: not persisted */ }
      syncThemeColor();
      describe();
    }

    btn.hidden = false;
    describe();
    syncThemeColor();            // a saved choice was applied by the inline script in <head>
    btn.addEventListener('click', function () { apply(current() === 'dark' ? 'light' : 'dark'); });

    // Follow system changes while the visitor has not chosen a theme.
    var sys = mq('(prefers-color-scheme: dark)');
    if (sys.addEventListener) { sys.addEventListener('change', describe); }
  })();

  /* 2. MOBILE NAVIGATION ------------------------ */
  (function mobileNav() {
    var btn = $('[data-nav-toggle]');
    var panel = $('[data-nav]');
    if (!btn || !panel) { return; }

    var header = btn.closest ? btn.closest('.site-header') : null;
    var tools = $('.site-header__tools');
    var bar = $('.site-header__bar');

    function setOpen(open) {
      root.classList.toggle('nav-open', open);                 // site.css draws the scrim
      panel.setAttribute('data-open', open ? 'true' : 'false');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    }
    function isOpen() { return btn.getAttribute('aria-expanded') === 'true'; }

    btn.hidden = false;
    setOpen(false);

    btn.addEventListener('click', function () { setOpen(!isOpen()); });
    panel.addEventListener('click', function (e) {
      if (e.target.closest && e.target.closest('a')) { setOpen(false); }
    });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen()) { setOpen(false); btn.focus(); }
    });
    doc.addEventListener('click', function (e) {
      if (isOpen() && !panel.contains(e.target) && !btn.contains(e.target)) { setOpen(false); }
    });
    // Tabbing past the last link closes the menu, so focus is never hidden behind the open panel.
    if (header) {
      header.addEventListener('focusout', function (e) {
        if (isOpen() && e.relatedTarget && !header.contains(e.relatedTarget)) { setOpen(false); }
      });
    }

    // From 64rem the index is drawn before the theme toggle (to its left in the bar, above it in
    // the rail). Move the controls after the index there, so Tab follows what the eye sees.
    if (header && tools && bar) {
      var wide = mq('(min-width: 64rem)');
      var place = function () {
        if (wide.matches) { setOpen(false); header.appendChild(tools); } else { bar.appendChild(tools); }
      };
      place();
      if (wide.addEventListener) { wide.addEventListener('change', place); }
    }
  })();

  /* 3. SCROLL FLAGS ------------------------
     Two things in the header repeat the hero, so site.css holds each back until the
     original has scrolled away:
       .past-masthead  the name in the top bar (below the rail breakpoint), after the <h1>
       .past-hero      "Email me" / "CV" in the rail, after the hero's own buttons */
  (function scrollFlags() {
    function flag(className, el) {
      if (!el || !('IntersectionObserver' in window)) { root.classList.add(className); return; }
      new IntersectionObserver(function (entries) {
        root.classList.toggle(className, !entries[entries.length - 1].isIntersecting);
      }, { rootMargin: '-56px 0px 0px 0px' }).observe(el);   // 56px = the sticky bar (--bar-h)
    }
    flag('past-masthead', $('#hero-name'));
    flag('past-hero', $('.hero__actions'));
  })();

  /* 4. ACTIVE SECTION ------------------------ */
  (function activeSection() {
    var links = $$('.index a[href^="#"]');
    if (!links.length || !('IntersectionObserver' in window)) { return; }

    var byId = {};
    var sections = [];
    links.forEach(function (a) {
      var id = decodeURIComponent(a.getAttribute('href').slice(1));
      var el = doc.getElementById(id);
      if (el) { byId[id] = a; sections.push(el); }
    });
    if (!sections.length) { return; }

    var visible = {};
    function update() {
      // The active section is the last one (in page order) crossing the reading line.
      var activeId = null;
      sections.forEach(function (s) { if (visible[s.id]) { activeId = s.id; } });
      links.forEach(function (a) { a.removeAttribute('aria-current'); });
      if (activeId && byId[activeId]) { byId[activeId].setAttribute('aria-current', 'true'); }
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting; });
      update();
    }, { rootMargin: '-35% 0px -60% 0px', threshold: 0 });
    sections.forEach(function (s) { io.observe(s); });
  })();

  /* 5. PUBLICATIONS ------------------------
     All items are in the HTML. Unfiltered, the list is clipped to the first
     CLIP items until "Show all" is pressed; any filter or search shows every
     match. Items are hidden with [hidden], which the print stylesheet overrides. */
  (function publications() {
    var form = $('[data-pub-filters]');
    var list = $('[data-pub-list]');
    if (!form || !list) { return; }

    var CLIP = mq('(min-width: 48rem)').matches ? 10 : 5;
    var items = $$('.pub', list);
    var typeBtns = $$('[data-pub-type]', form);
    var topicSel = $('[data-pub-topic]', form);
    var search = $('[data-pub-search]', form);
    var count = $('[data-pub-count]', form);
    var empty = $('[data-pub-empty]');
    var more = $('[data-pub-more]');               // wrapper of the "Show all" button
    var resets = $$('[data-pub-reset]');          // inline "Clear filters" + the one in the empty state
    var inlineReset = $('[data-pub-reset]', form);
    var moreBtn = more && $('button', more);
    var state = { type: 'all', topic: 'all', q: '' };
    var expanded = !moreBtn || items.length <= CLIP;

    // Search text: lower case, accents folded ("valencia" finds "València"), and the
    // non-breaking hyphens and spaces used for display turned back into plain ones.
    function fold(text) {
      text = text.toLowerCase().replace(/\u2011/g, '-').replace(/\s+/g, ' ');
      return text.normalize ? text.normalize('NFD').replace(/[\u0300-\u036f]/g, '') : text;
    }
    var haystack = items.map(function (item) {
      return fold($$('.pub__meta, .pub__title, .pub__authors, .pub__venue, .pub__note, .pub__topics', item)
        .map(function (el) {
          // Leave out screen-reader-only labels ("Topics:") so they are not searchable words.
          var copy = el.cloneNode(true);
          $$('.vh', copy).forEach(function (vh) { vh.parentNode.removeChild(vh); });
          return copy.textContent;
        }).join(' '));
    });

    function filtering() { return state.type !== 'all' || state.topic !== 'all' || state.q !== ''; }

    function matches(item, i) {
      if (state.type !== 'all' && item.getAttribute('data-type') !== state.type) { return false; }
      if (state.topic !== 'all') {
        var topics = (item.getAttribute('data-topics') || '').split('|');
        if (topics.indexOf(state.topic) === -1) { return false; }
      }
      if (state.q) {
        // every word typed must appear somewhere in the entry
        return state.q.split(' ').every(function (w) { return haystack[i].indexOf(w) !== -1; });
      }
      return true;
    }

    function render() {
      var clip = !expanded && !filtering();
      var shown = 0;
      items.forEach(function (item, i) {
        var ok = matches(item, i) && !(clip && i >= CLIP);
        item.hidden = !ok;
        if (ok) { shown++; }
      });
      if (count) { count.textContent = 'Showing ' + shown + ' of ' + items.length; }
      if (empty) { empty.hidden = shown !== 0; }
      if (more) { more.hidden = !clip; }
      if (inlineReset) { inlineReset.hidden = !filtering(); }
      list.hidden = shown === 0;
      typeBtns.forEach(function (b) {
        b.setAttribute('aria-pressed', b.getAttribute('data-pub-type') === state.type ? 'true' : 'false');
      });
    }

    function expand(focusItem) {
      expanded = true;
      render();
      if (focusItem) { focusItem.setAttribute('tabindex', '-1'); focusItem.focus({ preventScroll: true }); }
    }

    typeBtns.forEach(function (b) {
      b.addEventListener('click', function () { state.type = b.getAttribute('data-pub-type') || 'all'; render(); });
    });
    if (topicSel) {
      topicSel.addEventListener('change', function () { state.topic = topicSel.value || 'all'; render(); });
    }
    if (search) {
      search.addEventListener('input', function () { state.q = fold(search.value).trim(); render(); });
    }
    resets.forEach(function (btn) {
      btn.addEventListener('click', function () {
        state = { type: 'all', topic: 'all', q: '' };
        if (topicSel) { topicSel.value = 'all'; }
        if (search) { search.value = ''; search.focus(); }
        render();
      });
    });
    if (moreBtn) {
      // Keyboard and screen-reader users continue from the first newly shown item.
      moreBtn.addEventListener('click', function () { expand(items[CLIP]); });
    }
    form.addEventListener('submit', function (e) { e.preventDefault(); });

    // A link straight to a clipped publication (index.html#pub-...) opens the list.
    function showLinked() {
      var id;
      try { id = decodeURIComponent((location.hash || '#').slice(1)); } catch (e) { return; }   // malformed %-escape
      var target = id && doc.getElementById(id);
      if (target && target.hidden && list.contains(target)) { expand(); target.scrollIntoView(); }
    }
    window.addEventListener('hashchange', showLinked);

    form.hidden = false;
    render();
    showLinked();
  })();

  /* 6. COPY ADDRESS ------------------------ */
  (function copyAddress() {
    var btn = $('[data-copy]');
    if (!btn || !navigator.clipboard || !navigator.clipboard.writeText) { return; }
    var label = $('[data-copy-label]', btn);
    var status = $('[data-copy-status]');
    var idle = label ? label.textContent : '';
    var timer;

    btn.hidden = false;
    btn.addEventListener('click', function () {
      navigator.clipboard.writeText(btn.getAttribute('data-copy')).then(function () {
        if (label) { label.textContent = 'Address copied'; }
        if (status) { status.textContent = 'Address copied'; }
        clearTimeout(timer);
        timer = setTimeout(function () {
          if (label) { label.textContent = idle; }
          if (status) { status.textContent = ''; }
        }, 2500);
      }, function () {
        if (status) { status.textContent = 'Could not copy. The address is ' + btn.getAttribute('data-copy'); }
      });
    });
  })();

  /* 7. LIGHTBOX (photographs, award certificates) ------------------------
     Any element with data-lightbox="<name>" is a group; inside it, each link with data-w / data-h
     (= native pixels of its full-size JPEG) opens a modal <dialog> instead of the file: showModal()
     keeps focus inside and closes on Esc; this block adds Previous / Next (buttons, arrow keys,
     swipe) within the group, the "n of 12" count, the scroll lock, and hands focus back to the
     link that opened it. The caption is the link's data-caption, or the <figcaption> beside it. */
  (function lightbox() {
    var groups = $$('[data-lightbox]').map(function (el) {
      return { name: el.getAttribute('data-lightbox') || 'Images', links: $$('a[data-w]', el) };
    }).filter(function (g) { return g.links.length; });
    if (!groups.length || !window.HTMLDialogElement || !HTMLDialogElement.prototype.showModal) { return; }

    var box, source, img, caption, count, nav;                // the dialog is built the first time it is needed
    var links = [];                                           // the open group's links
    var current = 0;
    var opener = null;
    var touchX = null;

    function icon(name) { return '<svg width="16" height="16" aria-hidden="true" focusable="false"><use href="#i-' + name + '"/></svg>'; }

    function webp(link) { return link.getAttribute('href').replace(/\.jpg$/, '.webp'); }

    function show(i) {
      current = (i + links.length) % links.length;            // wraps round at either end
      var link = links[current];
      source.removeAttribute('srcset');                        // both, or the last photo stays up under the new
      img.removeAttribute('src');                              // caption until the next one has downloaded
      img.width = link.getAttribute('data-w');
      img.height = link.getAttribute('data-h');
      img.alt = $('img', link).alt;
      source.srcset = webp(link);
      img.src = link.getAttribute('href');
      var fig = $('figcaption', link.parentNode);
      caption.textContent = link.getAttribute('data-caption') || (fig ? fig.textContent : '');
      // The live region names the photograph as well: "2 of 12: Mukutmanipur, West Bengal"
      var n = links.length > 1 ? (current + 1) + ' of ' + links.length : '';   // a lone certificate needs no count
      count.textContent = n;
      var place = doc.createElement('span');
      place.className = 'vh';
      place.textContent = (n ? ': ' : '') + caption.textContent;
      count.appendChild(place);
    }

    function build() {
      box = doc.createElement('dialog');
      box.className = 'lightbox';
      box.setAttribute('aria-label', 'Photographs');
      box.setAttribute('aria-describedby', 'lightbox-caption');  // so the first photograph is named on opening
      box.innerHTML =
        '<div class="lightbox__bar">' +
          '<p class="lightbox__count" role="status"></p>' +
          '<button class="btn btn--secondary btn--small" type="button" data-close>Close' + icon('close') + '</button>' +
        '</div>' +
        '<figure class="lightbox__stage">' +
          '<picture><source type="image/webp"><img alt=""></picture>' +
          '<figcaption id="lightbox-caption"></figcaption>' +
        '</figure>' +
        '<div class="lightbox__nav">' +
          '<button class="btn btn--secondary btn--small" type="button" data-step="-1">' + icon('prev') + 'Previous</button>' +
          '<button class="btn btn--secondary btn--small" type="button" data-step="1">Next' + icon('next') + '</button>' +
        '</div>';
      doc.body.appendChild(box);
      source = $('source', box);
      img = $('img', box);
      caption = $('figcaption', box);
      count = $('.lightbox__count', box);
      nav = $('.lightbox__nav', box);
      // Once a photograph is up, fetch the next one so that Next is immediate.
      img.addEventListener('load', function () { new Image().src = webp(links[(current + 1) % links.length]); });

      box.addEventListener('click', function (e) {
        var step = e.target.closest('[data-step]');
        if (step) { show(current + Number(step.getAttribute('data-step'))); return; }
        // Close button, or a click on the empty paper around the photograph
        if (e.target.closest('[data-close]') || e.target === box || e.target.classList.contains('lightbox__stage')) { box.close(); }
      });
      box.addEventListener('keydown', function (e) {
        if (links.length > 1) {
          if (e.key === 'ArrowLeft') { show(current - 1); } else if (e.key === 'ArrowRight') { show(current + 1); }
        }
        if (e.key !== 'Tab') { return; }
        // Tab wraps round inside the dialog instead of leaving for the browser's own controls.
        var stops = $$('button', box);
        var edge = e.shiftKey ? stops[0] : stops[stops.length - 1];
        if (doc.activeElement === edge) { e.preventDefault(); stops[e.shiftKey ? stops.length - 1 : 0].focus(); }
      });
      box.addEventListener('touchstart', function (e) { touchX = e.touches.length === 1 ? e.touches[0].clientX : null; }, { passive: true });
      box.addEventListener('touchend', function (e) {
        if (touchX === null) { return; }
        var dx = e.changedTouches[0].clientX - touchX;
        touchX = null;
        if (Math.abs(dx) > 48 && links.length > 1) { show(current + (dx < 0 ? 1 : -1)); }
      }, { passive: true });
      box.addEventListener('close', function () {                // fires however it was closed: button, Esc or a click on the paper
        root.classList.remove('lightbox-open');
        if (opener) { opener.focus(); }
      });
    }

    groups.forEach(function (group) {
      group.links.forEach(function (link, i) {
        link.addEventListener('click', function (e) {
          if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) { return; }   // new tab / window / download: leave to the browser
          e.preventDefault();
          if (!box) { build(); }
          links = group.links;
          box.setAttribute('aria-label', group.name);
          nav.hidden = links.length < 2;                       // a single certificate has nothing to step through
          opener = link;
          show(i);
          root.classList.add('lightbox-open');
          box.showModal();
        });
      });
    });
  })();

  /* 8. REVEAL ON SCROLL ------------------------ */
  (function reveal() {
    var targets = $$('[data-reveal]');
    if (!targets.length || !('IntersectionObserver' in window)) { return; }
    if (mq('(prefers-reduced-motion: reduce)').matches) { return; }

    // Whatever is already on screen (or above it) stays as it is: only content further down fades in.
    var below = targets.filter(function (t) {
      if (t.getBoundingClientRect().top < window.innerHeight) { t.classList.add('is-in'); return false; }
      return true;
    });
    root.classList.add('reveal-on');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.01 });
    below.forEach(function (t) { io.observe(t); });

    // Safety net: never leave content hidden (e.g. a jump to the end of the page, printing).
    window.addEventListener('beforeprint', function () {
      targets.forEach(function (t) { t.classList.add('is-in'); });
    });
  })();
})();
