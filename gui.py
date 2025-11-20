import sys
import requests
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox

class App(QWidget):
    def __init__(self):
        super().__init__()
        #App Layout
        self.setWindowTitle("Simple File Converter")

        layout = QVBoxLayout()

        self.label = QLabel("No file selected")
        layout.addWidget(self.label)

        self.btn_pick = QPushButton("Choose File")
        self.btn_pick.clicked.connect(self.pick)
        layout.addWidget(self.btn_pick)

        self.format_box = QComboBox()
        self.format_box.addItems(["pdf", "jpg", "png", "docx"])
        layout.addWidget(self.format_box)

        self.btn_convert = QPushButton("Convert")
        self.btn_convert.clicked.connect(self.convert)
        self.btn_convert.setEnabled(False)
        layout.addWidget(self.btn_convert)

        self.setLayout(layout)
        self.file_path = None

    def pick(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pick a file")
        if path:
            self.file_path = path
            self.label.setText(path)
            self.btn_convert.setEnabled(True)

    def convert(self):
        url = "http://127.0.0.1:5000/convert"
        target = self.format_box.currentText()

        with open(self.file_path, 'rb') as f:
            files = {'file': f}
            data = {'target': target}
            resp = requests.post(url, files=files, data=data)

        if resp.status_code == 200:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Converted File", f"output.{target}")
            if save_path:
                with open(save_path, 'wb') as out:
                    out.write(resp.content)
        else:
            self.label.setText("Conversion failed")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec())