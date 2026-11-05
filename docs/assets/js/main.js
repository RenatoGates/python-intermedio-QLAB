(function () {
  "use strict";

  var header = document.querySelector(".site-header");
  var nav = document.getElementById("siteNav");
  var navToggle = document.getElementById("navToggle");
  var navLinks = nav ? Array.prototype.slice.call(nav.querySelectorAll("a")) : [];

  /* ---------- Year ---------- */
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---------- Header state ---------- */
  function onScroll() {
    if (header) header.classList.toggle("scrolled", window.scrollY > 12);
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---------- Mobile nav ---------- */
  function closeNav() {
    if (!nav || !navToggle) return;
    nav.classList.remove("open");
    navToggle.setAttribute("aria-expanded", "false");
    navToggle.setAttribute("aria-label", "Abrir menú");
  }

  if (navToggle && nav) {
    navToggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", String(open));
      navToggle.setAttribute("aria-label", open ? "Cerrar menú" : "Abrir menú");
    });

    navLinks.forEach(function (link) {
      link.addEventListener("click", closeNav);
    });

    document.addEventListener("click", function (e) {
      if (!nav.classList.contains("open")) return;
      if (!nav.contains(e.target) && !navToggle.contains(e.target)) closeNav();
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 900) closeNav();
    });
  }

  /* ---------- Active nav link ---------- */
  var sections = ["inicio", "sobre-mi", "experiencia", "proyectos", "certificados", "contacto"]
    .map(function (id) { return document.getElementById(id); })
    .filter(Boolean);

  var navByHash = {};
  navLinks.forEach(function (link) {
    var href = link.getAttribute("href") || "";
    if (href.charAt(0) === "#") navByHash[href.slice(1)] = link;
  });

  if ("IntersectionObserver" in window && sections.length) {
    var activeObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        navLinks.forEach(function (l) { l.classList.remove("active"); });
        var link = navByHash[entry.target.id];
        if (link) link.classList.add("active");
      });
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });
    sections.forEach(function (s) { activeObserver.observe(s); });
  }

  /* ---------- Reveal on scroll ---------- */
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach(function (el) { revealObserver.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("in-view"); });
  }

  /* ---------- PDF modal ---------- */
  var modal = document.getElementById("pdfModal");
  var frame = document.getElementById("pdfFrame");
  var modalTitle = document.getElementById("pdfModalTitle");
  var openLink = document.getElementById("pdfOpen");
  var downloadLink = document.getElementById("pdfDownload");
  var fallback = document.getElementById("pdfFallback");
  var closeBtn = modal ? modal.querySelector(".modal-close") : null;
  var lastFocused = null;

  function openModal(pdf, title) {
    if (!modal || !frame) return;
    lastFocused = document.activeElement;
    modalTitle.textContent = title || "Certificado";
    frame.src = pdf + "#view=FitH&toolbar=1";
    openLink.href = pdf;
    downloadLink.href = pdf;
    fallback.href = pdf;
    modal.hidden = false;
    document.body.classList.add("modal-open");
    if (closeBtn) closeBtn.focus();
  }

  function closeModal() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    frame.src = "about:blank";
    document.body.classList.remove("modal-open");
    if (lastFocused && typeof lastFocused.focus === "function") lastFocused.focus();
  }

  document.querySelectorAll(".cert-card").forEach(function (card) {
    card.addEventListener("click", function () {
      openModal(card.getAttribute("data-pdf"), card.getAttribute("data-title"));
    });
  });

  if (modal) {
    modal.querySelectorAll("[data-close]").forEach(function (el) {
      el.addEventListener("click", closeModal);
    });

    document.addEventListener("keydown", function (e) {
      if (modal.hidden) return;
      if (e.key === "Escape") {
        closeModal();
        return;
      }
      if (e.key !== "Tab") return;

      var focusables = modal.querySelectorAll("a[href], button:not([disabled]), iframe");
      if (!focusables.length) return;
      var first = focusables[0];
      var last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    });
  }

  /* ---------- Copy email ---------- */
  var copyBtn = document.getElementById("copyEmail");
  var toast = document.getElementById("toast");
  var toastTimer = null;

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove("show"); }, 2200);
  }

  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      var email = copyBtn.getAttribute("data-email") || "renatogates2124@gmail.com";

      function done() { showToast("Correo copiado: " + email); }
      function fail() { showToast("No se pudo copiar. Escribe a " + email); }

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(email).then(done).catch(function () {
          fallbackCopy(email) ? done() : fail();
        });
      } else {
        fallbackCopy(email) ? done() : fail();
      }
    });
  }

  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.top = "-1000px";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (err) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  /* ---------- Smooth scroll for older browsers ---------- */
  if (!("scrollBehavior" in document.documentElement.style)) {
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
      link.addEventListener("click", function (e) {
        var id = link.getAttribute("href");
        if (!id || id === "#") return;
        var target = document.querySelector(id);
        if (!target) return;
        e.preventDefault();
        window.scrollTo(0, target.getBoundingClientRect().top + window.pageYOffset - 90);
      });
    });
  }
})();
