// Access-code gate: asks once per browser session, then every AI request carries the code.
// index.html calls accessHeaders() when it sends a question or a recording, and accessRequired() when the server answers 401.
(function () {
  var KEY = "fa-access";
  function saved() { try { return sessionStorage.getItem(KEY) || ""; } catch (e) { return ""; } }
  function keep(code) { try { sessionStorage.setItem(KEY, code); } catch (e) {} }
  function forget() { try { sessionStorage.removeItem(KEY); } catch (e) {} }
  function check(code) {
    return fetch("/access/check", { headers: code ? { "X-Access-Code": code } : {} }).then(function (r) { return r.json(); });
  }
  function el(tag, css, text) { var n = document.createElement(tag); if (css) n.style.cssText = css; if (text) n.textContent = text; return n; }

  window.accessHeaders = function () { var c = saved(); return c ? { "X-Access-Code": c } : {}; };

  var open = null;                                   // the overlay while it is on screen
  window.accessRequired = function (message) {
    if (open) { if (message) open.msg.textContent = message; return; }
    var wrap = el("div", "position:fixed;inset:0;z-index:99999;background:#0d0f12;display:flex;align-items:center;justify-content:center;padding:16px;font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif");
    wrap.setAttribute("role", "dialog"); wrap.setAttribute("aria-modal", "true"); wrap.setAttribute("aria-labelledby", "fa-acc-title");
    var card = el("form", "width:100%;max-width:380px;background:#1b212a;border:1px solid #2f3946;border-radius:12px;padding:24px;display:flex;flex-direction:column;gap:14px;color:#ecEFF3");
    var title = el("h1", "margin:0;font-size:1.25rem", "Fire Emergency Assistant"); title.id = "fa-acc-title";
    var lead = el("p", "margin:0;color:#aab3bf;line-height:1.45", "Enter the access code from your company to open the assistant.");
    var label = el("label", "font-size:.9rem;color:#aab3bf", "Access code"); label.setAttribute("for", "fa-acc-input");
    var input = el("input", "font:inherit;padding:12px;border-radius:8px;border:1px solid #4a5666;background:#12161c;color:#ecEFF3;min-height:44px");
    input.id = "fa-acc-input"; input.type = "password"; input.autocomplete = "off"; input.required = true;
    var msg = el("div", "min-height:1.2em;color:#ff8a70;font-size:.9rem"); msg.setAttribute("role", "alert");
    var btn = el("button", "font:inherit;font-weight:700;padding:12px;border-radius:8px;border:0;background:#f05a33;color:#14100e;min-height:44px;cursor:pointer", "Open");
    btn.type = "submit";
    var sos = el("p", "margin:0;padding-top:12px;border-top:1px solid #2f3946;color:#ecEFF3;font-size:.95rem", "In an emergency call 112 first.");
    msg.textContent = message || "";
    card.append(title, lead, label, input, msg, btn, sos); wrap.appendChild(card); document.body.appendChild(wrap);
    open = { wrap: wrap, msg: msg };
    input.focus();
    card.addEventListener("submit", function (e) {
      e.preventDefault(); var code = input.value.trim(); if (!code) return;
      btn.disabled = true; msg.textContent = "";
      check(code).then(function (d) {
        if (d.ok) { keep(code); wrap.remove(); open = null; }
        else { msg.textContent = "Wrong code. Please try again."; input.select(); }
      }).catch(function () { msg.textContent = "Could not reach the server. Try again."; })
        .then(function () { btn.disabled = false; });
    });
  };

  // On load: ask for the code only when the server wants one and the saved one is missing or wrong.
  check(saved()).then(function (d) { if (d.required && !d.ok) { forget(); window.accessRequired(""); } }).catch(function () {});
})();