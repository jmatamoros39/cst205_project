import os
import sys
import requests
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox

class App(QWidget):
    def __init__(self):
        super().__init__()
        #App Layout
        self.setWindowTitle("Img and Document File Converter")

        layout = QVBoxLayout()

        self.label = QLabel("No file selected")
        layout.addWidget(self.label)

        self.btn_pick = QPushButton("Choose File")
        self.btn_pick.clicked.connect(self.pick)
        layout.addWidget(self.btn_pick)


        self.labelCon = QLabel("Convert to...")
        layout.addWidget(self.labelCon)

        self.format_box = QComboBox()
        layout.addWidget(self.format_box)

        self.btn_convert = QPushButton("Convert")
        self.btn_convert.clicked.connect(self.convert)
        self.btn_convert.setEnabled(False)
        layout.addWidget(self.btn_convert)

        self.LineLabel = QLabel("---------------------------------------------------------------------------------------")
        layout.addWidget(self.LineLabel)

        # Windows Instructions
        self.winLabel = QLabel("<b>Windows Instructions: ")
        layout.addWidget(self.winLabel)

        self.winLabel1 = QLabel("      In a Command Prompt run: set CONVERTAPI_SECRET=(Your_sandbox_token_here)")
        layout.addWidget(self.winLabel1)

        self.winLabel2 = QLabel("      then run cst205app.py in the same window and cst205gui.py in a seperate one")
        layout.addWidget(self.winLabel2)

        #Mac Instructions
        self.macLabel = QLabel("<b>Mac/Linux Instructions: ")
        layout.addWidget(self.macLabel)

        self.macLabel1 = QLabel("      In Terminal run: export CONVERTAPI_SECRET = your_sandbox_token_here")
        layout.addWidget(self.macLabel1)

        self.macLabel2 = QLabel("      then run cst205app.py in the same window and cst205gui.py in a seperate one")
        layout.addWidget(self.macLabel2)

        #Capabilities
        self.macLabel = QLabel("<b>Mac/Linux Instructions: ")
        layout.addWidget(self.macLabel)
        


        self.setLayout(layout)
        self.file_path = None

        self.conversionMap = {
        # Images
            '.png': ['jpg', 'pdf', 'gif', 'bmp', 'webp', 'ico'],
            '.jpg': ['png', 'pdf', 'gif', 'bmp', 'webp', 'ico'],
            '.jpeg': ['png', 'pdf', 'gif', 'bmp', 'webp', 'ico'],
            '.gif': ['png', 'jpg', 'pdf', 'bmp', 'webp'],
            '.bmp': ['png', 'jpg', 'pdf', 'gif', 'webp'],
            '.ico': ['png', 'jpg', 'bmp', 'gif'], 
            '.webp': ['png', 'jpg', 'pdf', 'gif'],

        # Documents
            '.pdf': ['docx', 'jpg', 'png', 'txt'],
            '.docx': ['pdf', 'txt', 'html'],
            '.doc': ['pdf', 'docx', 'txt', 'html'],
            '.txt': ['pdf', 'docx', 'html'],
            '.html': ['pdf', 'docx', 'txt'],
            
        }

    def pick(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pick a file")
        if path:
            self.file_path = path
            self.label.setText(path)

            file_ext = os.path.splitext(path)[1].lower()

            self.format_box.clear()
            if file_ext in self.conversionMap:
                self.format_box.addItems(self.conversionMap[file_ext])
                self.btn_convert.setEnabled(True)
            else:
                self.format_box.addItem("No Conversion Available")
                self.btn_convert.setEnabled(False)

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