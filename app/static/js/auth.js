// Account page — sign in / sign up / reset password / Google, via the auth API.

(function () {
    "use strict";

    var i18n = window.APP_I18N || {};
    var AUTH = "/api/v1/auth";
    var HOME = "/api/v1/notes/";

    function $(id) { return document.getElementById(id); }

    window.setLanguage = function (lang) {
        document.cookie = "locale=" + lang + ";path=/;max-age=31536000";
        window.location.reload();
    };

    function alertBox(msg, ok) {
        var el = $("alert");
        el.textContent = msg;
        el.className = "alert show " + (ok ? "ok" : "err");
    }
    function clearAlert() { $("alert").className = "alert"; }

    var MODES = ["login", "register", "forgot"];
    window.showMode = function (mode) {
        clearAlert();
        MODES.forEach(function (m) {
            var form = $(m + "Form");
            if (form) form.classList.toggle("active", m === mode);
        });
        $("tabLogin").classList.toggle("active", mode === "login");
        $("tabRegister").classList.toggle("active", mode === "register");
    };

    // sign in
    $("loginForm").addEventListener("submit", function (e) {
        e.preventDefault();
        var email = $("loginEmail").value.trim();
        var password = $("loginPassword").value;
        if (!email || !password) { alertBox(i18n.needFields, false); return; }

        var body = new URLSearchParams();
        body.append("username", email);
        body.append("password", password);

        fetch(AUTH + "/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: body.toString()
        })
            .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
            .then(function (res) {
                if (res.ok && res.d.access_token) {
                    localStorage.setItem("access_token", res.d.access_token);
                    alertBox(i18n.loginOk, true);
                    setTimeout(function () { window.location.href = HOME; }, 700);
                } else {
                    alertBox(i18n.loginFail, false);
                }
            })
            .catch(function () { alertBox(i18n.loginFail, false); });
    });

    // sign up
    $("registerForm").addEventListener("submit", function (e) {
        e.preventDefault();
        var email = $("regEmail").value.trim();
        var password = $("regPassword").value;
        if (!email || !password) { alertBox(i18n.needFields, false); return; }

        fetch(AUTH + "/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email, password: password })
        })
            .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
            .then(function (res) {
                if (res.ok) {
                    alertBox(i18n.registerOk, true);
                    setTimeout(function () { showMode("login"); }, 900);
                } else {
                    var msg = i18n.registerFail;
                    if (res.d && res.d.detail && typeof res.d.detail === "string") msg = res.d.detail;
                    alertBox(msg, false);
                }
            })
            .catch(function () { alertBox(i18n.registerFail, false); });
    });

    // forgot password (server always answers 202, never reveals if email exists)
    $("forgotForm").addEventListener("submit", function (e) {
        e.preventDefault();
        var email = $("forgotEmail").value.trim();
        if (!email) { alertBox(i18n.needFields, false); return; }

        fetch(AUTH + "/forgot-password", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email })
        }).finally(function () { alertBox(i18n.forgotOk, true); });
    });

    // Google OAuth — needs real client id/secret in .env
    window.loginWithGoogle = function () {
        fetch(AUTH + "/google/authorize")
            .then(function (r) { return r.json(); })
            .then(function (d) {
                if (d.authorization_url) {
                    window.location.href = d.authorization_url;
                } else {
                    alertBox(i18n.googleFail, false);
                }
            })
            .catch(function () { alertBox(i18n.googleFail, false); });
    };
})();
