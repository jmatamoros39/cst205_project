import sys
import tempfile
import os
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QComboBox, QFrame,
    QSizePolicy, QProgressBar, QMessageBox, QSplashScreen, QInputDialog, 
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtGui import QIcon

import requests

VIDEO_FORMATS = ["mp4", "mov", "avi", "mkv", "webm", "wmv"]
DOC_FORMATS = ["pdf", "jpg", "png", "docx"]
RES_MAP = {"480p": 480, "720p": 720, "1080p": 1080}

# --- ConversionThread for FFmpeg ---
class ConversionThread(QThread):
    progress = Signal(int)
    finished = Signal(bytes, str)
    error = Signal(str)

    def __init__(self, input_path, target_ext, resolution):
        super().__init__()
        self.input_path = input_path
        self.target_ext = target_ext
        self.resolution = resolution

    def run(self):
        try:
            if self.target_ext in VIDEO_FORMATS:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{self.target_ext}") as tmp:
                    output_path = tmp.name

                scale_args = []
                if self.resolution != "original":
                    scale_args = ["-vf", f"scale=-2:{RES_MAP[self.resolution]}"]

                cmd = ["ffmpeg", "-y", "-i", self.input_path, *scale_args, output_path]

                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                )

                total_duration = self.get_video_duration(self.input_path)

                while True:
                    line = process.stderr.readline()
                    if not line:
                        break
                    if "time=" in line:
                        try:
                            time_str = line.split("time=")[1].split(" ")[0]
                            h, m, s = map(float, time_str.split(":"))
                            seconds = h * 3600 + m * 60 + s
                            percent = int((seconds / total_duration) * 100)
                            self.progress.emit(min(percent, 100))
                        except:
                            pass

                process.wait()
                if process.returncode != 0:
                    self.error.emit("FFmpeg conversion failed")
                    return

                with open(output_path, "rb") as f:
                    content = f.read()
                self.finished.emit(content, f"converted.{self.target_ext}")
                os.remove(output_path)

            else:  # Non-video file
                import convertapi
                api_key = os.environ.get("CONVERTAPI_SECRET") or "YOUR_CONVERTAPI_KEY"
                convertapi.api_secret = api_key

                result = convertapi.convert(self.target_ext, {"File": self.input_path})
                output_path = result.file.save(tempfile.gettempdir())
                with open(output_path, "rb") as f:
                    content = f.read()
                self.finished.emit(content, f"converted.{self.target_ext}")
                os.remove(output_path)

        except Exception as e:
            self.error.emit(str(e))

    @staticmethod
    def get_video_duration(path):
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", path
            ]
            output = subprocess.check_output(cmd).decode().strip()
            duration = float(output)
            return max(duration, 1.0)
        except Exception:
            return 1.0

class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Converter")
        self.setWindowIcon(QIcon("img/fileconverter_logo.ico"))
        self.setMinimumSize(450, 280)
        self.file_path = None
        self.is_video = False
        self.converted_content = None
        self.converted_name = None
        self.thread = None

        self.setWindowTitle("File Converter")
        self.setMinimumSize(450, 280)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title = QLabel("File Converter")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Choose a file, pick a format, and convert it using the backend.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # File picker
        file_row = QHBoxLayout()
        self.label = QLabel("No file selected")
        self.label.setObjectName("PathLabel")
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.btn_pick = QPushButton("Browse…")
        self.btn_pick.clicked.connect(self.pick)

        file_row.addWidget(self.label)
        file_row.addWidget(self.btn_pick)
        main_layout.addLayout(file_row)

        # Format/resolution
        row2 = QHBoxLayout()
        self.format_box = QComboBox()
        self.format_box.currentTextChanged.connect(self.update_resolution_enabled)

        self.resolution_box = QComboBox()
        self.resolution_box.addItem("original")
        self.resolution_box.setEnabled(False)

        self.btn_convert = QPushButton("Convert")
        self.btn_convert.clicked.connect(self.convert)
        self.btn_convert.setEnabled(False)

        row2.addWidget(QLabel("Convert to:"))
        row2.addWidget(self.format_box)
        row2.addWidget(QLabel("Resolution:"))
        row2.addWidget(self.resolution_box)
        row2.addStretch()
        row2.addWidget(self.btn_convert)
        main_layout.addLayout(row2)

        # Progress bar implemented (hid by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel("Select a file to get started.")
        self.status_label.setObjectName("StatusLabel")
        main_layout.addWidget(self.status_label)

        main_layout.addStretch()
        self.setLayout(main_layout)

        # Style
        self.setStyleSheet("""
            QWidget {
                font-family: Segoe UI, Arial;
                font-size: 11pt;
            }
            #TitleLabel {
                font-size: 18pt;
                font-weight: bold;
            }
            #PathLabel {
                color: #555;
            }
            #StatusLabel {
                color: #2c7a7b;
            }
            QPushButton {
                padding: 6px 14px;
                border-radius: 6px;
                background-color: #1976d2;
                color: white;
            }
            QPushButton:disabled {
                background-color: #9e9e9e;
            }
            QPushButton:hover:!disabled {
                background-color: #1565c0;
            }
            QComboBox {
                padding: 4px 8px;
            }
        """)

    def pick(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pick a file")
        if not path:
            return

        self.file_path = path
        self.label.setText(path)
        self.btn_convert.setEnabled(True)

        ext = path.split(".")[-1].lower()
        self.is_video = ext in VIDEO_FORMATS

        self.format_box.clear()
        self.resolution_box.clear()
        self.resolution_box.addItem("original")

        if self.is_video:
            self.format_box.addItems(VIDEO_FORMATS)
            self.load_video_resolutions(path)
        else:
            self.format_box.addItems(DOC_FORMATS)
            self.resolution_box.setEnabled(False)

    def load_video_resolutions(self, path):
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=height",
                "-of", "csv=p=0",
                path
            ]
            output = subprocess.check_output(cmd).decode().strip()
            src_h = int(output)

            allowed = ["original"]
            if src_h >= 480: allowed.append("480p")
            if src_h >= 720: allowed.append("720p")
            if src_h >= 1080: allowed.append("1080p")

            self.resolution_box.clear()
            self.resolution_box.addItems(allowed)
            self.resolution_box.setEnabled(True)
        except:
            self.resolution_box.clear()
            self.resolution_box.addItem("original")
            self.resolution_box.setEnabled(True)

    def update_resolution_enabled(self):
        ext = self.format_box.currentText()
        if self.is_video and ext in VIDEO_FORMATS:
            self.resolution_box.setEnabled(True)
        else:
            self.resolution_box.setEnabled(False)

    # Conversion
    def convert(self):
        if not self.file_path:
            return

        # Disable convert button to prevent multiple clicks
        self.btn_convert.setEnabled(False)

        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.status_label.setText("Converting...")

        self.thread = ConversionThread(
            input_path=self.file_path,
            target_ext=self.format_box.currentText(),
            resolution=self.resolution_box.currentText()
        )

        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.on_conversion_finished)
        self.thread.error.connect(self.on_conversion_error)
        self.thread.start()

    def on_conversion_finished(self, content, name):
        self.converted_content = content
        self.converted_name = name
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.status_label.setText("Conversion complete!")
        self.btn_convert.setEnabled(True)  # Re-enable button
        self.ask_save_or_email()

    def on_conversion_error(self, message):
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.status_label.setText(message)
        self.btn_convert.setEnabled(True)  # Re-enable button
        QMessageBox.critical(self, "Error", message)

    # --- Save or Email ---
    def ask_save_or_email(self):
        choice = QMessageBox.question(
            self,
            "Save or Email",
            "Do you want to save the file locally or send it via email?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Ok
            )

        if choice == QMessageBox.StandardButton.Save:
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Converted File", self.converted_name
            )
            if save_path:
                with open(save_path, "wb") as f:
                    f.write(self.converted_content)
                QMessageBox.information(self, "Saved", f"File saved to {save_path}")

        elif choice == QMessageBox.StandardButton.Ok:
            self.send_email_dialog()

    def send_email_dialog(self):
        email, ok = QInputDialog.getText(self, "Send Email", "Recipient email:")
        if not ok or not email:
            return
        message, ok = QInputDialog.getText(self, "Send Email", "Enter message:")
        if not ok:
            return

        url = "http://127.0.0.1:5000/send"
        files = {'file': (self.converted_name, self.converted_content)}
        data = {'receiver_email': email, 'message': message}

        try:
            resp = requests.post(url, files=files, data=data)
            if resp.status_code == 200:
                QMessageBox.information(self, "Email Sent", "Email sent successfully!")
            else:
                QMessageBox.critical(self, "Error", f"Failed to send email: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send email: {e}")

# --- Splash screen ---
def show_splash(app):
    width, height = 500, 250

    # Load your logo
    logo = QPixmap("img/csumb_logo.jpg")  # Replace with your logo path
    # Scale to fit within splash without cutting off
    logo = logo.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    # Create a pixmap for the splash
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.white)  # fallback background color

    # Paint the logo with opacity, centered
    from PySide6.QtGui import QPainter
    painter = QPainter(pixmap)
    painter.setOpacity(0.1)  # semi-transparent
    # Center the logo
    x = (width - logo.width()) // 2
    y = (height - logo.height()) // 2
    painter.drawPixmap(x, y, logo)
    painter.setOpacity(1.0)  # reset for text
    painter.end()

    # Create the splash screen
    splash = QSplashScreen(pixmap)
    splash.setFont(QFont("Tahoma", 28, QFont.Bold))
    splash.showMessage("File Converter", alignment=Qt.AlignCenter, color=Qt.black)

    # Center splash on screen
    screen_geo = app.primaryScreen().geometry()
    splash.move((screen_geo.width() - width) // 2, (screen_geo.height() - height) // 2)
    splash.show()
    return splash


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("img/fileconverter_logo.ico"))

    splash = show_splash(app)

    main_window = None
    def open_main():
        global main_window
        main_window = App()
        main_window.show()
        splash.close()

    QTimer.singleShot(2000, open_main)
    sys.exit(app.exec())
