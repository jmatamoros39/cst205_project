#CONVERTAPI_KEY = "JEpzAAk0CMDmgE4VxQRS7FJJJspbUqa6"
#APYHUB_KEY = "APY0IHz0YzdOK7uOtarLINsIzb7PmjCYoYwnb7bGoJp7z8YmEjXMuNVigNCzEh3gRX8cdDTP"
from flask import Flask, request, send_file
import tempfile
import os
import subprocess
import convertapi

app = Flask(__name__)

# === HARDCODED KEYS ===
CONVERTAPI_KEY = "JEpzAAk0CMDmgE4VxQRS7FJJJspbUqa6"

convertapi.api_secret = CONVERTAPI_KEY
convertapi.api_credentials = CONVERTAPI_KEY

VIDEO_FORMATS = ["mp4", "mov", "avi", "mkv", "webm", "wmv"]
DOC_FORMATS = ["pdf", "jpg", "png", "docx"]

@app.route('/convert', methods=['POST'])
def convert_file():
    try:
        file = request.files['file']
        target_ext = request.form.get('target_ext', '').lower()

        file_ext = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            file.save(tmp.name)
            input_path = tmp.name

        # Video conversion using FFmpeg
        if target_ext in VIDEO_FORMATS:
            output_path = os.path.join(tempfile.gettempdir(), f"converted.{target_ext}")
            cmd = [
                "ffmpeg",
                "-y",  # overwrite
                "-i", input_path,
                output_path
            ]
            subprocess.run(cmd, check=True)
            return send_file(output_path, as_attachment=True)

        # Non-video conversion using ConvertAPI
        result = convertapi.convert(target_ext, {'File': input_path})
        output_path = result.file.save(tempfile.gettempdir())
        return send_file(output_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        return f"FFmpeg error: {e}", 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error: {e}", 500

if __name__ == "__main__":
    print("Flask server running at http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
