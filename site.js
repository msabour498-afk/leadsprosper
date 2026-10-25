/* Leads Prosper site script: menus, forms, and dataLayer events. */
(function () {
  "use strict";
  var CFG = window.LP_CONFIG || {};
  window.dataLayer = window.dataLayer || [];
  function track(event, data) {
    var payload = { event: event };
    for (var k in data) if (Object.prototype.hasOwnProperty.call(data, k)) payload[k] = data[k];
    window.dataLayer.push(payload);
  }
  window.lpTrack = track;

  /* ---------- Menus ---------- */
  var navToggle = document.querySelector(".nav-toggle");
  var navPanel = document.getElementById("nav-panel");
  var toggles = Array.prototype.slice.call(document.querySelectorAll(".menu-toggle"));

  function closeMenus(except) {
    toggles.forEach(function (t) {
      if (t === except) return;
      t.setAttribute("aria-expanded", "false");
      var m = document.getElementById(t.getAttribute("aria-controls"));
      if (m) m.classList.remove("open");
    });
  }
  function setNav(open) {
    if (!navToggle || !navPanel) return;
    navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    navToggle.textContent = open ? "Close" : "Menu";
    navPanel.classList.toggle("open", open);
    if (!open) closeMenus();
  }

  toggles.forEach(function (t) {
    var menu = document.getElementById(t.getAttribute("aria-controls"));
    t.addEventListener("click", function () {
      var open = t.getAttribute("aria-expanded") !== "true";
      closeMenus(t);
      t.setAttribute("aria-expanded", open ? "true" : "false");
      menu.classList.toggle("open", open);
    });
    t.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        closeMenus(t);
        t.setAttribute("aria-expanded", "true");
        menu.classList.add("open");
        var first = menu.querySelector("a");
        if (first) first.focus();
      }
    });
    menu.addEventListener("keydown", function (e) {
      var links = Array.prototype.slice.call(menu.querySelectorAll("a"));
      var i = links.indexOf(document.activeElement);
      if (e.key === "ArrowDown") { e.preventDefault(); links[(i + 1) % links.length].focus(); }
      if (e.key === "ArrowUp") { e.preventDefault(); links[(i - 1 + links.length) % links.length].focus(); }
      if (e.key === "Escape") {
        e.preventDefault();
        t.setAttribute("aria-expanded", "false");
        menu.classList.remove("open");
        t.focus();
      }
    });
  });

  if (navToggle) {
    navToggle.addEventListener("click", function () {
      setNav(navToggle.getAttribute("aria-expanded") !== "true");
    });
  }

  document.addEventListener("click", function (e) {
    if (!e.target.closest(".has-menu")) closeMenus();
    if (navPanel && navPanel.classList.contains("open") && !e.target.closest(".site-header")) setNav(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var openToggle = toggles.filter(function (t) { return t.getAttribute("aria-expanded") === "true"; })[0];
    if (openToggle) { closeMenus(); openToggle.focus(); return; }
    if (navPanel && navPanel.classList.contains("open")) { setNav(false); navToggle.focus(); }
  });
  document.addEventListener("focusin", function (e) {
    if (!e.target.closest(".has-menu")) closeMenus();
  });

  /* ---------- Contact click tracking ---------- */
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[href^='mailto:'], a[href^='tel:'], a[href^='sms:']");
    if (!a) return;
    var href = a.getAttribute("href");
    var method = href.indexOf("mailto:") === 0 ? "email" : href.indexOf("tel:") === 0 ? "phone" : "sms";
    var where = a.closest(".float-contact") ? "floating_button" : a.closest(".site-footer") ? "footer" : a.closest(".site-header") ? "header" : "page";
    track("contact_click", { contact_method: method, link_location: where, page_path: location.pathname });
  });

  /* ---------- Forms ---------- */
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  function splitName(full) {
    var parts = full.trim().replace(/\s+/g, " ").split(" ");
    var first = parts.shift() || "";
    return { first: first, last: parts.join(" ") };
  }
  function getCookie(name) {
    var m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[1]) : "";
  }
  function fieldValue(form, name) {
    var els = form.querySelectorAll("[name='" + name + "']");
    if (!els.length) return "";
    var el = els[0];
    if (el.type === "checkbox") {
      return Array.prototype.filter.call(els, function (x) { return x.checked; }).map(function (x) { return x.value; }).join(", ");
    }
    if (el.type === "radio") {
      var c = Array.prototype.filter.call(els, function (x) { return x.checked; })[0];
      return c ? c.value : "";
    }
    return (el.value || "").trim();
  }

  function validate(form) {
    var ok = true, firstBad = null;
    form.querySelectorAll("[data-required]").forEach(function (wrap) {
      var name = wrap.getAttribute("data-required");
      var val = fieldValue(form, name);
      var bad = !val;
      if (!bad && name === "email") bad = !EMAIL_RE.test(val);
      if (!bad && name === "name") bad = val.length < 2;
      if (!bad && name === "website") bad = !/\.[a-z]{2,}/i.test(val);
      wrap.classList.toggle("invalid", bad);
      var input = wrap.querySelector("input, select, textarea");
      if (input) input.setAttribute("aria-invalid", bad ? "true" : "false");
      if (bad) { ok = false; if (!firstBad) firstBad = input; }
    });
    if (firstBad) firstBad.focus();
    return ok;
  }

  function buildPayload(form) {
    var name = splitName(fieldValue(form, "name"));
    var extras = [];
    form.querySelectorAll("[data-extra]").forEach(function (el) {
      var key = el.getAttribute("data-extra");
      var n = el.getAttribute("data-name");
      var v = fieldValue(form, n);
      if (v) extras.push(key + ": " + v);
    });
    var notes = fieldValue(form, "message");
    var msg = extras.join("\n");
    if (notes) msg += (msg ? "\n\n" : "") + notes;
    return {
      firstname: name.first,
      lastname: name.last,
      email: fieldValue(form, "email"),
      phone: fieldValue(form, "phone"),
      message: msg
    };
  }

  function sendHubspot(p, formId) {
    var hs = CFG.form;
    var host = hs.hubspotRegion === "eu1" ? "api-eu1.hsforms.com" : "api.hsforms.com";
    var fields = ["firstname", "lastname", "email", "phone", "message"].filter(function (k) { return p[k]; })
      .map(function (k) { return { objectTypeId: "0-1", name: k, value: p[k] }; });
    var body = { fields: fields, context: { pageUri: location.href, pageName: document.title } };
    var hutk = getCookie("hubspotutk");
    if (hutk) body.context.hutk = hutk;
    return fetch("https://" + host + "/submissions/v3/integration/submit/" + hs.hubspotPortalId + "/" + hs.hubspotFormId, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body)
    }).then(function (r) { if (!r.ok) throw new Error("HubSpot " + r.status); });
  }
  function sendFormspree(p, formId) {
    var data = { first_name: p.firstname, last_name: p.lastname, email: p.email, phone: p.phone, message: p.message, form: formId, page: location.pathname };
    return fetch(CFG.form.formspreeEndpoint, {
      method: "POST", headers: { "Content-Type": "application/json", "Accept": "application/json" }, body: JSON.stringify(data)
    }).then(function (r) { if (!r.ok) throw new Error("Formspree " + r.status); });
  }
  function sendMailto(p, formId) {
    var subject = (formId === "audit" ? "Free audit request" : "Website message") + " from " + (p.firstname + " " + p.lastname).trim();
    var body = "Name: " + (p.firstname + " " + p.lastname).trim() + "\nEmail: " + p.email + (p.phone ? "\nPhone: " + p.phone : "") + "\n\n" + p.message;
    window.location.href = "mailto:" + CFG.email + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
    return Promise.resolve();
  }

  document.querySelectorAll("form[data-lead-form]").forEach(function (form) {
    var formId = form.getAttribute("data-lead-form");
    var status = form.querySelector(".form-status");
    var button = form.querySelector("button[type='submit']");

    // Prefill from query string (used by future free tools: ?tool=...&result=...).
    var params = new URLSearchParams(location.search);
    var toolName = params.get("tool");
    var toolResult = params.get("result");
    var msgBox = form.querySelector("[name='message']");
    if (toolName && msgBox && !msgBox.value) {
      msgBox.value = "From the " + toolName + " tool" + (toolResult ? ": " + toolResult : "") + "\n";
    }

    form.querySelectorAll("input, select, textarea").forEach(function (el) {
      el.addEventListener("input", function () {
        var wrap = el.closest("[data-required]");
        if (wrap && wrap.classList.contains("invalid")) validate(form);
      });
      el.addEventListener("change", function () {
        var wrap = el.closest("[data-required]");
        if (wrap && wrap.classList.contains("invalid")) validate(form);
      });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      status.textContent = "";
      status.className = "form-status";
      if (fieldValue(form, "company_fax")) return; // spam trap
      if (!validate(form)) {
        status.textContent = "Check the highlighted fields.";
        status.className = "form-status err";
        return;
      }
      var p = buildPayload(form);
      var provider = (CFG.form && CFG.form.provider) || "mailto";
      var send = provider === "hubspot" ? sendHubspot : provider === "formspree" ? sendFormspree : sendMailto;
      button.disabled = true;
      var label = button.textContent;
      button.textContent = "Sending...";
      send(p, formId).then(function () {
        track("generate_lead", { form_id: formId, form_destination: provider, page_path: location.pathname });
        var done = document.createElement("div");
        done.className = "form-done";
        done.setAttribute("tabindex", "-1");
        done.setAttribute("role", "status");
        var h = document.createElement("h2");
        var t = document.createElement("p");
        if (provider === "mailto") {
          h.textContent = "Almost done, " + p.firstname + ".";
          t.textContent = "Your email app should open with your details filled in. Press send there to reach us. If nothing opened, email " + CFG.email + ".";
        } else {
          h.textContent = "Thanks, " + p.firstname + ". We got it.";
          t.textContent = formId === "audit"
            ? "We'll review what you sent and reply by email at " + p.email + "."
            : "We'll reply by email at " + p.email + ".";
        }
        done.appendChild(h);
        done.appendChild(t);
        form.replaceWith(done);
        done.focus();
      }).catch(function () {
        button.disabled = false;
        button.textContent = label;
        status.textContent = "That didn't go through. Try again, or email " + CFG.email + ".";
        status.className = "form-status err";
      });
    });
  });
})();
