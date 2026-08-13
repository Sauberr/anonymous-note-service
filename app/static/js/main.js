// Index page — create / receive note logic.
// Translated strings are provided by the template via window.APP_I18N.

(function () {
    "use strict";

    var i18n = window.APP_I18N || {};

    function $(id) { return document.getElementById(id); }

    // language switch
    window.setLanguage = function (lang) {
        document.cookie = "locale=" + lang + ";path=/;max-age=31536000";
        window.location.reload();
    };

    // show selected file name
    var fileInput = $("noteImage");
    if (fileInput) {
        fileInput.addEventListener("change", function () {
            var name = this.files && this.files.length ? this.files[0].name : i18n.selectPicture;
            $("fileName").textContent = name;
        });
    }

    // create note
    var noteForm = $("noteForm");
    if (noteForm) {
        noteForm.addEventListener("submit", function (event) {
            event.preventDefault();
            var formData = new FormData(noteForm);

            var hours = parseInt($("lifetimeHours").value, 10) || 0;
            var minutes = parseInt($("lifetimeMinutes").value, 10) || 0;
            var seconds = parseInt($("lifetimeSeconds").value, 10) || 0;
            var totalSeconds = hours * 3600 + minutes * 60 + seconds;

            if ($("ephemeral").checked && totalSeconds > 0) {
                alert(i18n.ephemeralLifetime);
                return;
            }

            fetch("/api/v1/notes/create_note", { method: "POST", body: formData })
                .then(function (response) {
                    if (!response.ok) {
                        return response.json().then(function (data) {
                            throw new Error(data.detail || i18n.createError);
                        });
                    }
                    return response.json();
                })
                .then(function (data) {
                    if (data.response === "ok") {
                        document.location.href = "/api/v1/notes/result/" + data.note_id;
                    } else if (data.error) {
                        alert(data.error);
                    }
                })
                .catch(function (error) {
                    console.error("Error:", error);
                    alert(error.message);
                });

            noteForm.reset();
            $("fileName").textContent = i18n.selectPicture;
        });
    }

    // receive note
    var getNoteForm = $("getNoteForm");
    if (getNoteForm) {
        getNoteForm.addEventListener("submit", function (event) {
            event.preventDefault();
            var formData = new FormData();
            formData.append("note_id", $("noteId").value);
            formData.append("note_secret", $("getSecretPhrase").value);

            fetch("/api/v1/notes/get_note", { method: "POST", body: formData })
                .then(function (response) { return response.json(); })
                .then(function (data) {
                    if (data.response === "ok") {
                        var url = "/api/v1/notes/note_page/" + encodeURIComponent(data.note_final_text);
                        if (data.note_image) {
                            url += "?note_image=" + encodeURIComponent(data.note_image);
                        }
                        window.location.href = url;
                    } else {
                        alert(data.note_final_text || i18n.genericError);
                    }
                })
                .catch(function (error) {
                    console.error("Error:", error);
                    alert(i18n.requestError);
                });
        });
    }
})();
