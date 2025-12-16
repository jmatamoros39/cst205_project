from flask import Flask, request, send_file
from flask_mail import Mail, Message
from config import (
    EMAIL_USERNAME,
    EMAIL_PASSWORD,
    EMAIL_SERVER,
    EMAIL_PORT,
    EMAIL_USE_TLS,
    EMAIL_USE_SSL,
    API_KEY,
)
import convertapi
import os
import tempfile
import subprocess

print("Starting Flask backend...")

# Check for ConvertAPI token
api_key = os.environ.get("CONVERTAPI_SECRET")
api_key = api_key if api_key else API_KEY

if not api_key:
    print(
        "ERROR: ConvertAPI token not found. Set CONVERTAPI_SECRET environment variable or hardcode it."
    )
    # Optionally, hardcode for testing:
    # api_key = "your_sandbox_or_production_token_here"
    exit(1)

convertapi.api_secret = api_key
convertapi.api_credentials = api_key

app = Flask(__name__)

# Configure email
app.config["MAIL_SERVER"] = EMAIL_SERVER
app.config["MAIL_PORT"] = EMAIL_PORT
app.config["MAIL_USERNAME"] = EMAIL_USERNAME
app.config["MAIL_PASSWORD"] = EMAIL_PASSWORD
app.config["MAIL_USE_TLS"] = EMAIL_USE_TLS
app.config["MAIL_USE_SSL"] = EMAIL_USE_SSL
mail = Mail(app)

# Define video formats
VIDEO_FORMATS = ["mp4", "mov", "avi", "mkv", "webm", "wmv"]
DOC_FORMATS = ["pdf", "jpg", "png", "docx", "gif", "bmp", "webp", "ico", "txt", "html", "doc"]
RES_MAP = {"480p": 480, "720p": 720, "1080p": 1080}


@app.route("/video-info", methods=["POST"])
def video_info():
    """Get video resolution information"""
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

        # Determine allowed resolutions
        allowed = ["original"]
        if height >= 480:
            allowed.append("480p")
        if height >= 720:
            allowed.append("720p")
        if height >= 1080:
            allowed.append("1080p")

        os.unlink(path)  # Clean up temp file
        
        return {"width": width, "height": height, "allowed_resolutions": allowed}

    except Exception as e:
        print(f"Error getting video info: {e}")
        return {"error": str(e)}, 400


@app.route("/convert", methods=["POST"])
def convert_file():
    try:
        file = request.files["file"]
        target = request.form.get("target", "pdf")
        targetExt = request.form.get("targetExt", target).lower()
        requested_res = request.form.get("resolution", "original")

        # Save input file temporarily WITH the original extension
        file_ext = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            file.save(tmp.name)
            input_path = tmp.name

        # Video conversion using FFmpeg
        if targetExt in VIDEO_FORMATS:
            try:
                # Get source resolution
                cmd_probe = [
                    "ffprobe",
                    "-v", "error",
                    "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-of", "csv=p=0",
                    input_path
                ]
                result = subprocess.check_output(cmd_probe).decode().strip()
                src_w, src_h = map(int, result.split(","))
                
                # Prevent upscaling
                if requested_res in RES_MAP and src_h < RES_MAP[requested_res]:
                    os.unlink(input_path)
                    return f"Source video is {src_h}p. Cannot convert to {requested_res}.", 400

                # Build FFmpeg command
                scale_args = []
                if requested_res in RES_MAP:
                    scale_args = ["-vf", f"scale=-2:{RES_MAP[requested_res]}"]

                output_path = os.path.join(tempfile.gettempdir(), f"converted.{targetExt}")
                cmd = ["ffmpeg", "-y", "-i", input_path, *scale_args, output_path]

                print(f"Running FFmpeg: {' '.join(cmd)}")
                subprocess.run(cmd, check=True, capture_output=True)
                
                os.unlink(input_path)  # Clean up input file
                
                print(f"Video conversion successful: {input_path} -> {output_path}")
                return send_file(output_path, as_attachment=True)
                
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg error: {e}")
                print(f"FFmpeg stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
                os.unlink(input_path)
                return f"FFmpeg error: {e}", 500
            except Exception as e:
                print(f"Video conversion error: {e}")
                os.unlink(input_path)
                return f"Error: {e}", 500

        # Document/Image conversion using ConvertAPI
        else:
            try:
                result = convertapi.convert(targetExt, {"File": input_path})
                output_path = result.file.save(tempfile.gettempdir())

                os.unlink(input_path)  # Clean up input file
                
                print(f"Conversion successful: {input_path} -> {output_path}")
                return send_file(output_path, as_attachment=True)
                
            except Exception as e:
                print("ConvertAPI error:", e)
                os.unlink(input_path)
                return f"ConvertAPI error: {e}", 500

    except Exception as e:
        print("Error during conversion:", e)
        import traceback
        traceback.print_exc()
        return f"Error: {e}", 500


# Sending files via email
@app.route("/send", methods=["POST"])
def send_email():
    receiverEmail = request.form.get("receiverEmail")
    receiver_email = request.form.get("receiver_email")  # Support both naming conventions
    messages = request.form.get("messages")
    message = request.form.get("message")  # Support both naming conventions
    file = request.files.get("file")

    # Use whichever naming convention was provided
    receiverEmail = receiverEmail or receiver_email
    messages = messages or message

    print(f"Form data: {request.form}")
    print(f"Files: {request.files}")
    print(f"File object: {file}")

    if not receiverEmail or not messages:
        return "Missing required fields", 400

    try:
        msg = Message(
            "[Selkie Converter] Your file has been converted 📁",
            sender=EMAIL_USERNAME,
            recipients=[receiverEmail],
        )
        msg.body = messages

        if file:  # Attach file if provided
            print("send_email(): Attaching file to email")
            msg.attach(
                filename=file.filename, 
                content_type=file.content_type or "application/octet-stream", 
                data=file.read()
            )
        else:
            print("send_email(): No file attached to email.")

        mail.send(msg)
        print(f"Email sent successfully to {receiverEmail}")
        return "Email sent", 200

    except Exception as e:
        print("Error sending email:", e)
        import traceback
        traceback.print_exc()
        return f"Error sending email: {e}", 500


if __name__ == "__main__":
    print("Flask server running on http://127.0.0.1:5000")
    print("✓ Document conversion: Enabled (ConvertAPI)")
    print("✓ Video conversion: Enabled (FFmpeg)")
    print("✓ Email functionality: Enabled")
    app.run(host="127.0.0.1", port=5000, debug=True)
