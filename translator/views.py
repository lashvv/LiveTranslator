import os
from dotenv import load_dotenv
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from google import genai
from pathlib import Path
import time

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
            save_path = os.path.join(settings.BASE_DIR, 'temp_audio.webm')

            with open(save_path, 'wb+') as destination:
                for chunk in audio.chunks():
                    destination.write(chunk)

            uploaded_file = client.files.upload(
                file=save_path,
                config={"mime_type": "audio/webm"}
            )

            # Wait for Google to finish processing the file before using it
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(0.5)
                uploaded_file = client.files.get(name=uploaded_file.name)

            if uploaded_file.state.name == "FAILED":
                return JsonResponse({"error": "File processing failed"}, status=500)

            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[
                    uploaded_file,
                    "Transcribe the speech in this audio exactly as spoken, in Georgian. Return only the transcription, nothing else."
                ]
            )

            transcript = response.text.strip()

            print("Transcript:", transcript)

            return JsonResponse({
                "status": "received",
                "transcript": transcript
            })

    return JsonResponse({
        "error": "No file received"
    }, status=400)