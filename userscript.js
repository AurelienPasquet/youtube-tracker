// ==UserScript==
// @name         YouTube Tracker Flask (amélioré)
// @namespace    yt-tracker
// @version      1.1
// @description  Track YouTube watch time and send to Flask server (avec heartbeat + détection navigation)
// @match        https://www.youtube.com/*
// @grant        none
// ==/UserScript==

(function() {
    let startTime = null;
    let videoElement = null;

    // Envoi d'une session au serveur Flask
    function logSession() {
        if (startTime && videoElement) {
            const now = Date.now();
            const sessionTime = Math.round((now - startTime) / 1000); // secondes
            startTime = null;

            const title = document.title.replace(" - YouTube", "");
            const url = window.location.href;

            fetch("http://localhost:5000/log", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title: title,
                    url: url,
                    session_time: sessionTime
                })
            }).catch(err => console.error("Erreur envoi Flask:", err));

            console.log(`[YT Tracker] ${title} (${url}) : +${sessionTime}s`);
        }
    }

    // Attacher les listeners sur le player vidéo
    function attachTracker(video) {
        if (videoElement === video) return; // déjà attaché
        videoElement = video;

        video.addEventListener("play", () => {
            startTime = Date.now();
        });

        video.addEventListener("pause", logSession);
        video.addEventListener("ended", logSession);

        window.addEventListener("beforeunload", logSession);

        console.log("[YT Tracker] Tracker attaché au player");
    }

    // ✅ Heartbeat : toutes les 30s, on sauvegarde
    setInterval(() => {
        if (startTime) {
            logSession();
            startTime = Date.now(); // redémarrer le compteur
        }
    }, 30_000);

    // ✅ Navigation interne (SPA YouTube → changement d’URL sans rechargement complet)
    function patchHistoryMethod(method) {
        const orig = history[method];
        return function() {
            logSession(); // log avant changement
            return orig.apply(this, arguments);
        };
    }
    history.pushState = patchHistoryMethod("pushState");
    history.replaceState = patchHistoryMethod("replaceState");
    window.addEventListener("popstate", logSession);

    // Surveiller le DOM pour détecter le player vidéo
    const observer = new MutationObserver(() => {
        const video = document.querySelector("video");
        if (video) attachTracker(video);
    });

    observer.observe(document.body, { childList: true, subtree: true });
})();
