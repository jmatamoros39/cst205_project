# Selkie Converter
# Authors: Anthony Cervantes, Jiyun Go, Jose Matamoros, Alex Hernandez

#Purpose
The Selkie Conversion app is a desktop app used to:
- Convert video files (MP4, MOV, AVI, MKV, WebM, WMV)
- Convert document files (PDF, JPG, PNG, DOCX) using ConvertAPI
- Resize videos to standard resolutions (480p, 720p, 1080p)
- Save converted files locally or send them via email

App is extremley user friendly relying on FFmpeg and ConverAPI for conversions

## Technology Used
- **Frontend:** PySide6 (Qt for Python)
- **Backend:** Flask API
- **Video Processing:** FFmpeg
- **Document Conversion:** ConvertAPI
- **Email:** Flask-Mail with Gmail SMTP

## Prerequisites:
Copy Sandbox Token: jbhQRLOaLhH2RxyLv0SOchX65KKu0t2x 

Open Virtual machine 
Install flask-mail: pip install flask-mail 
Install FFmpeg for video conversion

## Windows(PowerShell): 
In Command Prompt run: set CONVERTAPI_SECRET=(your_sandbox_token_here) 
Run python cst205app.py in the same window 
Run python cst205gui.py in a separate window 

## Mac/Linux: 
In Terminal run: export CONVERTAPI_SECRET=(your_sandbox_token_here) 
Run python3 cst205app.py in the same window 
Run python3 cst205gui.py in a separate window 

## Directory Setup
README.md (Optional)
app.py
gui.py
config.py
icons/SelkieSplashwBkg.mp4
Fonts/nexaround-trial-glow.otf

## Supported Conversions: 
Images: PNG, JPG, GIF, BMP, ICO, WEBP
Documents: PDF, DOCX, DOC, TXT, HTML
Videos: MP4, MOV, AVI, MKV, WEBM, WMV (with resolution options)

*Built for educational and personal use.*
