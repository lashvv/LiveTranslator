import os
from dotenv import load_dotenv
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from google import genai
from pathlib import Path
from google.genai import types

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')
print("LOADED KEY:", os.environ.get("GEMINI_API_KEY"))
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
# Load the model once when the server starts, not on every request
# model = WhisperModel("small", device="cpu", compute_type="int8")

# Create your views here.
def index(request):
    return render(request, 'translator/index.html')

def upload_audio(request):
    if request.method == 'POST':
        audio = request.FILES.get('audio')

        if audio:
            audio_bytes = audio.read()

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/webm"),
                    "Transcribe EXACTLY what is said in this Georgian audio, word for word. "
                    "Do not correct grammar, do not paraphrase, do not summarize.\n"
                    "Respond with exactly two lines, nothing else:\n"
                    "Line 1: the exact Georgian transcript.\n"
                    "Line 2: the English translation of that transcript.\n"
                    "Do not add labels, numbering, or any other text."
                ],
                config={"temperature": 0}
            )

            lines = response.text.strip().split("\n")
            transcript = lines[0].strip() if len(lines) > 0 else ""
            translation = lines[1].strip() if len(lines) > 1 else ""

            print("Transcript:", transcript)
            print("Translation:", translation)

            return JsonResponse({
                "status": "received",
                "transcript": transcript,
                "translation": translation
            })

    return JsonResponse({
        "error": "No file received"
    }, status=400)