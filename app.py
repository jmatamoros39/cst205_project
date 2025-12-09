# app.py
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

app = Flask(__name__)

# Configure email
app.config["MAIL_SERVER"] = EMAIL_SERVER
app.config["MAIL_PORT"] = EMAIL_PORT
app.config["MAIL_USERNAME"] = EMAIL_USERNAME
app.config["MAIL_PASSWORD"] = EMAIL_PASSWORD
app.config["MAIL_USE_TLS"] = EMAIL_USE_TLS
app.config["MAIL_USE_SSL"] = EMAIL_USE_SSL
mail = Mail(app)


@app.route("/convert", methods=["POST"])
def convert_file():
    try:
        file = request.files["file"]
        target = request.form.get("target", "pdf")

        # Save input file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            input_path = tmp.name

        # Convert file
        result = convertapi.convert(target, {"File": input_path})
        output_path = result.file.save()

        print(f"Conversion successful: {input_path} -> {output_path}")
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        print("Error during conversion:", e)
        return f"Error: {e}", 500


if __name__ == "__main__":
    # Start Flask server and show messages
    print("Flask server running on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)


# Sending files via email
@app.route("/send", methods=["POST"])
def send_email():
    receiver_email = request.form.get("receiver_email")
    messages = request.form.get("messages")
    file = request.files.get("file")

    print(f"Form data: {request.form}")
    print(f"Files: {request.files}")
    print(f"File object: {file}")

    if not receiver_email or not messages:
        return "Missing required fields", 40

    try:
        msg = Message(
            "Converted File", sender=EMAIL_USERNAME, recipients=[receiver_email]
        )
        msg.body = messages

        if file:  # Attach file if provided
            print("!!!Attaching file to email!!!")
            msg.attach(
                filename=file.filename, content_type=file.content_type, data=file.read()
            )
        else:
            print("No file attached to email.")
        mail.send(msg)

    except Exception as e:
        print("Error sending email:", e)

    return "Email sent", 200
