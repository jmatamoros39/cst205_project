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

RES_MAP = {"480p": 480, "720p": 720, "1080p": 1080}


@app.route("/video-info", methods=["POST"])
def video_info():
    try:
        file = request.files["file"]
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            file.save(tmp.name)
            path = tmp.name

        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0",
            path
        ]
        result = subprocess.check_output(cmd).decode().strip()
        width, height = map(int, result.split(","))

        allowed = ["original"]
        if height >= 480:
            allowed.append("480p")
        if height >= 720:
            allowed.append("720p")
        if height >= 1080:
            allowed.append("1080p")

        return {"width": width, "height": height, "allowed_resolutions": allowed}

    except Exception as e:
        return {"error": str(e)}, 400


@app.route("/convert", methods=["POST"])
def convert_file():
    try:
        file = request.files["file"]
        target_ext = request.form.get("target_ext", "").lower()
        requested_res = request.form.get("resolution", "original")

        file_ext = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            file.save(tmp.name)
            input_path = tmp.name

        # Video conversion
        if target_ext in VIDEO_FORMATS:
            # Get source resolution
            cmd_probe = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "csv=p=0",
                input_path
            ]
            try:
                result = subprocess.check_output(cmd_probe).decode().strip()
                src_w, src_h = map(int, result.split(","))
            except Exception as e:
                return f"Error reading video resolution: {e}", 500

            # Prevent upscaling
            if requested_res in RES_MAP and src_h < RES_MAP[requested_res]:
                return f"Source video is {src_h}p. Cannot convert to {requested_res}.", 400

            scale_args = []
            if requested_res in RES_MAP:
                scale_args = ["-vf", f"scale=-2:{RES_MAP[requested_res]}"]

            output_path = os.path.join(tempfile.gettempdir(), f"converted.{target_ext}")
            cmd = ["ffmpeg", "-y", "-i", input_path, *scale_args, output_path]

            try:
                subprocess.run(cmd, check=True)
                return send_file(output_path, as_attachment=True)
            except subprocess.CalledProcessError as e:
                return f"FFmpeg error: {e}", 500

        # Non-video conversion using ConvertAPI
        if target_ext in DOC_FORMATS:
            try:
                result = convertapi.convert(target_ext, {"File": input_path})
                output_path = result.file.save(tempfile.gettempdir())
                return send_file(output_path, as_attachment=True)
            except Exception as e:
                return f"ConvertAPI error: {e}", 500

        return f"Invalid target format: {target_ext}", 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error: {e}", 500


if __name__ == "__main__":
    print("Flask server running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
