import sys
import tempfile
import os
import shutil
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QComboBox, QFrame,
    QSizePolicy, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal

VIDEO_FORMATS = ["mp4", "mov", "avi", "mkv", "webm", "wmv"]
DOC_FORMATS = ["pdf", "jpg", "png", "docx"]
RES_MAP = {"480p": 480, "720p": 720, "1080p": 1080}


class ConversionThread(QThread):
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, input_path, target_ext, resolution, output_path):
        super().__init__()
        self.input_path = input_path
        self.target_ext = target_ext
        self.resolution = resolution
        self.output_path = output_path

    def run(self):
        if self.target_ext in VIDEO_FORMATS:
            scale_args = []
            if self.resolution in RES_MAP:
                scale_args = ["-vf", f"scale=-2:{RES_MAP[self.resolution]}"]

            cmd = ["ffmpeg", "-y", "-i", self.input_path, *scale_args, self.output_path]

            try:
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
                            pass  # skip parsing errors

                process.wait()
                if process.returncode != 0:
                    self.error.emit("FFmpeg conversion failed")
                else:
                    self.progress.emit(100)
                    self.finished.emit(self.output_path)

            except Exception as e:
                self.error.emit(str(e))

        else:
            # Non-video conversion simulated progress bar
            for i in range(101):
                self.progress.emit(i)
                self.msleep(20)
            self.finished.emit(self.input_path)

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
            if duration <= 0:
                return 1.0
            return duration
        except Exception:
            return 1.0  # Fallback if ffprobe fails


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.is_video = False

        self.setWindowTitle("Simple File Converter")
        self.setMinimumSize(450, 280)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title = QLabel("Simple File Converter")
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

        # Pick file
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

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel("Select a file to get started.")
        self.status_label.setObjectName("StatusLabel")
        main_layout.addWidget(self.status_label)

        main_layout.addStretch()
        self.setLayout(main_layout)
        
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
            # Use ffprobe to get video height
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
            if src_h >= 480:
                allowed.append("480p")
            if src_h >= 720:
                allowed.append("720p")
            if src_h >= 1080:
                allowed.append("1080p")

            self.resolution_box.clear()
            self.resolution_box.addItems(allowed)
            self.resolution_box.setEnabled(True)
        except Exception:
            self.resolution_box.clear()
            self.resolution_box.addItem("original")
            self.resolution_box.setEnabled(True)

    def update_resolution_enabled(self):
        ext = self.format_box.currentText()
        if self.is_video and ext in VIDEO_FORMATS:
            self.resolution_box.setEnabled(True)
        else:
            self.resolution_box.setEnabled(False)

    def convert(self):
        if not self.file_path:
            return

        output_path = os.path.join(tempfile.gettempdir(), f"converted.{self.format_box.currentText()}")
        self.progress_bar.show()
        self.progress_bar.setValue(0)

        self.thread = ConversionThread(
            input_path=self.file_path,
            target_ext=self.format_box.currentText(),
            resolution=self.resolution_box.currentText(),
            output_path=output_path
        )

        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.on_conversion_finished)
        self.thread.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self.thread.start()
        self.status_label.setText("Converting...")

    def on_conversion_finished(self, output_path):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Converted File", os.path.basename(output_path))
        if save_path:
            shutil.copyfile(output_path, save_path)
            self.status_label.setText(f"Saved: {save_path}")
        else:
            self.status_label.setText("Save canceled.")
        self.progress_bar.setValue(0)
        self.progress_bar.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec())
