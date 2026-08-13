// Shared logic for the result and note pages.

(function () {
    "use strict";

    window.returnToRoot = function () {
        document.location.href = "/api/v1/notes/";
    };

    window.copyId = function () {
        var el = document.getElementById("noteId");
        if (!el) return;
        var text = el.textContent.trim();
        navigator.clipboard.writeText(text).then(function () {
            var msg = document.getElementById("copied");
            if (!msg) return;
            msg.classList.add("show");
            setTimeout(function () { msg.classList.remove("show"); }, 1600);
        });
    };
})();
