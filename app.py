# pylint: disable-all

import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from transformers import pipeline
import subprocess
import os

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load the Whisper model
asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-small")


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        # Ensure a file is provided
        if 'audio' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['audio']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Save the uploaded file
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(input_path)

        # Define output file path
        ts = datetime.datetime.now().isoformat().split('.')[0]
        outputfile = f'output-{ts}.wav'
        output_path = os.path.join(OUTPUT_FOLDER, outputfile)

        # Run FFmpeg to convert the file
        ffmpeg_command = [
            "ffmpeg", "-i", input_path,
            "-ac", "1", "-ar", "16000",  # Convert to mono, 16kHz
            output_path
        ]
        process = subprocess.run(
            ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Check for errors
        if process.returncode != 0:
            error_details = process.stderr.decode()
            return jsonify({"error": "FFmpeg conversion failed", "details": error_details}), 500

        # Transcribe
        return transcribe_audio(outputfile)
        

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


def transcribe_audio(filename):
    try:
        # Path to the file in the OUTPUT_FOLDER
        file_path = os.path.join(OUTPUT_FOLDER, filename)

        # Check if the file exists
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        # Read the audio file and perform transcription using the ASR pipeline
        result = asr_pipeline(file_path)

        # Return the transcribed text
        return jsonify({"transcription": result['text']}), 200

    except Exception as e:
        raise Exception("error: An error occurred during transcription", e)


if __name__ == '__main__':
    app.run(debug=True)
