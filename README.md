# LiveTranslator

An AI-powered live translation tool. A presenter speaks in Georgian, and the audience sees a live English translation appear on screen as they talk — no human interpreter needed.

By [Lasha Jincharadze](https://github.com/lashvv)

## How it works

The presenter's speech goes through a short, continuous loop:

1. **Capture** — the browser records the presenter's microphone in short audio chunks (~3 seconds each), using the browser's built-in `MediaRecorder` API.
2. **Send** — each chunk is sent to a Django backend as soon as it's recorded.
3. **Transcribe + Translate** — the backend sends the audio directly to Google's Gemini API in a single request, asking it to return both the exact Georgian transcript and its English translation.
4. **Display** — both the original and translated text are appended to the page live, so captions build up continuously as the presenter keeps talking.
5. **Repeat** — the next chunk starts recording immediately, so the cycle runs continuously for as long as the presenter keeps speaking.

```
Presenter mic
     |
Browser (MediaRecorder, 3s chunks)
     |
Django backend (/upload-audio/)
     |
Gemini API (transcribe + translate in one call)
     |
Live captions on screen (original + translated)
```

## Why there's always a small delay

This isn't instant translation, and it's not meant to be — no live translation system is, including human interpreters, who also lag a sentence or two behind the speaker. The realistic target here is a few seconds of delay per chunk. This is near real-time, not instant, and that's a deliberate design choice, not a limitation to apologize for.

## Tech stack

- **Backend:** Django
- **Frontend:** HTML, vanilla JavaScript (no framework, no build step)
- **AI:** Google Gemini API (`gemini-3.6-flash`) — handles both speech-to-text and translation in a single request per chunk
- **Audio capture:** Browser `MediaRecorder` API

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
```

Run the server:

```bash
python3 manage.py runserver
```

Open `http://127.0.0.1:8000/` in Chrome (required for microphone access), click **Start Listening**, and speak in Georgian.

## Development notes

**Why Gemini instead of a dedicated speech-to-text service?**
Gemini was already integrated for a separate document-translation project, so reusing that meant no new API keys or SDKs to figure out. It also turned out to handle Georgian well — better, in fact, than running Whisper locally.

**Why not local Whisper?**
Local Whisper (`faster-whisper`, running on CPU) was tried first. Georgian is a low-resource language in Whisper's training data, and the output was unusable — mixed scripts, hallucinated text, no real transcription. Gemini's broader multilingual training handled Georgian correctly out of the box. This was a real pivot made partway through development, after testing exposed the problem early rather than late.

**Why chunk-based instead of true streaming?**
True streaming (partial results appearing mid-sentence, refined as more audio arrives — like Zoom or Google Meet captions) needs a speech API built specifically for that. This project instead re-records and re-sends short, complete chunks in a loop. It's a solid approximation of "live," but it's the main architectural difference from a fully streaming production system.

**Model version mattered a lot.** Early testing used a preview model (`gemini-3-flash-preview`), which was slow and occasionally produced garbled or inconsistent transcripts. Switching to the stable release (`gemini-3.6-flash`) meaningfully improved both speed and transcription accuracy.

## Known limitations

- **Not true streaming** — captions update every few seconds in chunks, not word-by-word.
- **Chunk-boundary errors** — each chunk is transcribed independently with no memory of the previous chunk, so a sentence split across two chunks can occasionally lose accuracy at the boundary.
- **Single language pair** — currently Georgian → English only.
- **No speaker diarization** — doesn't distinguish between multiple speakers.
- **No audio output** — captions only, no text-to-speech dubbing.
- **Free-tier dependent** — relies on Gemini's free API tier, which has rate limits not suited for long-running or large-scale use.

## What's next

- A dedicated streaming speech-to-text provider (e.g. Deepgram, Google Cloud Speech-to-Text) for true word-by-word live captions and lower cost at scale.
- Speaker diarization for multiple presenters.
- A shared glossary of specific terms, so they translate consistently every time.
- Text-to-speech output, piping translated audio to headsets — the same pipeline with one more step at the end.
- Support for translating into multiple languages at once.
- Delivering captions to individual audience phones via QR code instead of one shared screen.