import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QComboBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = None

        # ---- Window basics ----
        self.setWindowTitle("Simple File Converter")
        self.setMinimumSize(450, 250)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ---- Header ----
        title = QLabel("Simple File Converter")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Choose a file, pick a format, and convert it using the backend.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # Divider line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # ---- File row ----
        file_row = QHBoxLayout()
        self.label = QLabel("No file selected")
        self.label.setObjectName("PathLabel")
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.btn_pick = QPushButton("Browse…")
        self.btn_pick.clicked.connect(self.pick)

        file_row.addWidget(self.label)
        file_row.addWidget(self.btn_pick)
        main_layout.addLayout(file_row)

        # ---- Format + convert row ----
        row2 = QHBoxLayout()
        fmt_text = QLabel("Convert to:")
        self.format_box = QComboBox()
        self.format_box.addItems(["pdf", "jpg", "png", "docx"])

        self.btn_convert = QPushButton("Convert")
        self.btn_convert.clicked.connect(self.convert)
        self.btn_convert.setEnabled(False)

        row2.addWidget(fmt_text)
        row2.addWidget(self.format_box)
        row2.addStretch()
        row2.addWidget(self.btn_convert)

        main_layout.addLayout(row2)

        # ---- Status ----
        self.status_label = QLabel("Select a file to get started.")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.status_label)

        # Add stretch so content stays near the top
        main_layout.addStretch()

        self.setLayout(main_layout)

        # Apply basic stylesheet
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
        if path:
            self.file_path = path
            self.label.setText(path)
            self.btn_convert.setEnabled(True)
            self.status_label.setText("Ready to convert.")

    def convert(self):
        if not self.file_path:
            self.status_label.setText("No file selected.")
            return

        url = "http://127.0.0.1:5000/convert"
        target = self.format_box.currentText()

        try:
            with open(self.file_path, 'rb') as f:
                files = {'file': f}
                data = {'target_ext': target}  # make sure this matches backend
                resp = requests.post(url, files=files, data=data, timeout=30)
        except requests.exceptions.RequestException as e:
            self.status_label.setText(f"Error: {e}")
            return

        if resp.status_code == 200:
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Converted File", f"output.{target}"
            )
            if save_path:
                with open(save_path, 'wb') as out:
                    out.write(resp.content)
                self.status_label.setText(f"Saved: {save_path}")
            else:
                self.status_label.setText("Save canceled.")
        else:
            self.status_label.setText("Conversion failed.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec())
