# 📁  File Converter App

**Authors:** Anthony Cervantes, Jiyun Go, Jose Matamoros, Alex Hernandez

### 👥 Team Roles
- **Backend Development:** Jose Matamoros, Jiyun Go
- **Frontend Development:** Anthony Cervantes, Alex Hernandez

<br>

## 📋 Overview

The **File Converter App** is a powerful desktop application that simplifies media and document conversion. Whether you need to convert videos, documents, or resize video files, this app has you covered.

### ✨ Key Features

- **Video Conversion** - Support for MP4, MOV, AVI, MKV, WebM, WMV formats
- **Document Conversion** - Handle PDF, JPG, PNG, DOCX files with ease
- **Video Resizing** - Scale videos to 480p, 720p, or 1080p resolutions
- **Flexible Output** - Save files locally or send them directly via email
- **Simple Interface** - Intuitive GUI built with PySide6

<br>

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | PySide6 (Qt for Python) |
| **Backend** | Flask API |
| **Video Processing** | FFmpeg |
| **Document Conversion** | ConvertAPI |
| **Email Service** | Flask-Mail with Gmail SMTP |

<br>

## 🚀 Setup Instructions

### 1️⃣ Install Required Software

Before getting started, ensure you have:

- **Python 3.10+** installed on your system
- **FFmpeg** downloaded and added to your system PATH
  - Download: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

### 2️⃣ Install Dependencies

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Core Dependencies:**
- Flask
- Flask-Mail
- PySide6
- requests
- convertapi
- filetype
- gmail-api

### 3️⃣ Configure Environment Variables

Set up your credentials before running the backend.

#### Windows PowerShell
```powershell
$env:EMAIL_USERNAME="your_email@gmail.com"
$env:EMAIL_PASSWORD="your_gmail_app_password"
$env:CONVERTAPI_SECRET="your_convertapi_key"
```

#### Windows CMD
```cmd
set EMAIL_USERNAME=your_email@gmail.com
set EMAIL_PASSWORD=your_gmail_app_password
set CONVERTAPI_SECRET=your_convertapi_key
```

#### macOS/Linux
```bash
export EMAIL_USERNAME="your_email@gmail.com"
export EMAIL_PASSWORD="your_gmail_app_password"
export CONVERTAPI_SECRET="your_convertapi_key"
```   
### 4️⃣ Run the Application

Start the backend server:
```bash
python app.py
```

In a new terminal, launch the GUI:
```bash
python gui.py
```

<br>

## 📖 How to Use

1. **Select a file** from your computer
2. **Choose the output format** or resolution
3. **Click Convert**
4. **Save locally** or **send via email**

