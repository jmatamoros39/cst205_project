# File Converter App
# Authors: Anthony Cervantes, Jiyun Go, Jose Matamoros, Alex Hernandez

## Purpose
The File Converter App is a desktop application that allows you to:
- Convert video files (MP4, MOV, AVI, MKV, WebM, WMV)
- Convert document files (PDF, JPG, PNG, DOCX) using ConvertAPI
- Resize videos to standard resolutions (480p, 720p, 1080p)
- Save converted files locally or send them via email

The app is simple to use and relies on FFmpeg and ConvertAPI for conversions.

## Technology Used
- **Frontend:** PySide6 (Qt for Python)
- **Backend:** Flask API
- **Video Processing:** FFmpeg
- **Document Conversion:** ConvertAPI
- **Email:** Flask-Mail with Gmail SMTP

## Setup Instructions

### 1. Install Required Software
- **Python 3.10+**
- **FFmpeg:** https://ffmpeg.org/download.html (add to system PATH)

### 2. Install Dependencies
Create a virtual environment:
```bash
python -m venv venv
```
Activate the virtual environment:
- **Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```
- **Windows (CMD):**
```cmd
venv\Scripts\activate
```
- **macOS/Linux:**
```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```
Dependencies include: Flask, Flask-Mail, PySide6, requests, convertapi, filetype

### 3. Configure Environment Variables
Set Gmail and ConvertAPI credentials before running the backend.

**PowerShell:**
```powershell
$env:EMAIL_USERNAME="your_email@gmail.com"
$env:EMAIL_PASSWORD="your_gmail_app_password"
$env:CONVERTAPI_SECRET="your_convertapi_key"
```

**CMD:**
```cmd
set EMAIL_USERNAME=your_email@gmail.com
set EMAIL_PASSWORD=your_gmail_app_password
set CONVERTAPI_SECRET=your_convertapi_key
```

**Notes:**
- Use a **Gmail app password** for EMAIL_PASSWORD. Generate it here: https://support.google.com/accounts/answer/185833?hl=en
- CONVERTAPI_SECRET is your personal ConvertAPI key: https://www.convertapi.com/

### 4. Run the App

1. Start the backend:
```bash
python app.py
```
2. Start the GUI:
```bash
python gui.py
```
3. Select a file, choose format/resolution, and convert.
4. Save locally or send via email.

## Important Notes
- Ensure FFmpeg is installed and accessible from the command line.
- Credentials are read from environment variables; do not hardcode them for security.
- The frontend does not require changes for credentials.
- Install `filetype` for file validation.

---
*Built for educational and personal use.*

