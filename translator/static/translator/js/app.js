const button = document.getElementById("start-btn");
const originalText = document.getElementById("original-text");

let recorder;
let stream;
let listening = false;
let fullTranscript = "";

async function startLoop() {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    listening = true;
    recordChunk();
}

function recordChunk() {
    if (!listening) return;

    let chunks = [];
    recorder = new MediaRecorder(stream);

    recorder.ondataavailable = event => {
        chunks.push(event.data);
    };

    recorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("audio", audioBlob, "speech.webm");

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch("/upload-audio/", {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken },
                body: formData
            });

            const result = await response.json();

            if (result.transcript) {
                fullTranscript += " " + result.transcript;
                originalText.innerText = fullTranscript;
            }
        } catch (err) {
            console.error("Upload failed:", err);
        }

        // immediately start the next chunk, whether this one succeeded or not
        recordChunk();
    };

    recorder.start();

    // 3 second chunks instead of 5 — tighter feel
    setTimeout(() => {
        if (recorder.state !== "inactive") {
            recorder.stop();
        }
    }, 3000);
}

button.addEventListener("click", () => {
    if (!listening) {
        startLoop();
        button.textContent = "Stop Listening";
    } else {
        listening = false;
        if (recorder && recorder.state !== "inactive") {
            recorder.stop();
        }
        stream.getTracks().forEach(track => track.stop());
        button.textContent = "Start Listening";
    }
});