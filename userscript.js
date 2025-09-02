// ==UserScript==
// @name         YouTube Tracker Flask
// @namespace    yt-tracker
// @version      1.1
// @description  Track YouTube watch time and send to Flask server (with heartbeat + navigation detection)
// @match        https://www.youtube.com/*
// @grant        none
// ==/UserScript==

(function() {
    let startTime = null;
    let videoElement = null;

    // Sending a session to the Flask server
    function logSession() {
        if (startTime && videoElement) {
            const now = Date.now();
            const sessionTime = Math.round((now - startTime) / 1000); // seconds
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
            }).catch(err => console.error("Flask sending error:", err));

            console.log(`[YT Tracker] ${title} (${url}) : +${sessionTime}s`);
        }
    }

    // Attach listeners to the video player
    function attachTracker(video) {
        if (videoElement === video) return; // already attached
        videoElement = video;

        video.addEventListener("play", () => {
            startTime = Date.now();
        });

        video.addEventListener("pause", logSession);
        video.addEventListener("ended", logSession);

        window.addEventListener("beforeunload", logSession);

        console.log("[YT Tracker] Tracker attached to the player");
    }

    // ✅ Heartbeat: we save every 30 seconds
    setInterval(() => {
        if (startTime) {
            logSession();
            startTime = Date.now(); // reset the counter
        }
    }, 30_000);

    // ✅ Internal navigation (YouTube SPA → URL change without full reload)
    function patchHistoryMethod(method) {
        const orig = history[method];
        return function() {
            logSession(); // log before change
            return orig.apply(this, arguments);
        };
    }
    history.pushState = patchHistoryMethod("pushState");
    history.replaceState = patchHistoryMethod("replaceState");
    window.addEventListener("popstate", logSession);

    // Monitor the DOM to detect the video player
    const observer = new MutationObserver(() => {
        const video = document.querySelector("video");
        if (video) attachTracker(video);
    });

    observer.observe(document.body, { childList: true, subtree: true });
})();
