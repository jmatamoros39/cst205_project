# app.py
from flask import Flask, request, send_file
import convertapi
import os
import tempfile

print("Starting Flask backend...")

# Check for ConvertAPI token
api_key = os.environ.get("CONVERTAPI_SECRET")
if not api_key:
    print("ERROR: ConvertAPI token not found. Set CONVERTAPI_SECRET environment variable or hardcode it.")
    # Optionally, hardcode for testing:
    # api_key = "your_sandbox_or_production_token_here"
    exit(1)

convertapi.api_secret = api_key

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_file():
    try:
        file = request.files['file']
        target = request.form.get('target', 'pdf')

        # Save input file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            input_path = tmp.name

        # Convert file
        result = convertapi.convert(target, {'File': input_path})
        output_path = result.file.save()

        print(f"Conversion successful: {input_path} -> {output_path}")
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        print("Error during conversion:", e)
        return f"Error: {e}", 500

if __name__ == '__main__':
    # Start Flask server and show messages
    print("Flask server running on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
