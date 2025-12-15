import os
import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QComboBox, QFrame, QSizePolicy, QTextEdit,
    QLineEdit, QMessageBox, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt, QUrl, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtGui import QColor, QPalette, QFontDatabase

class SplashScreen(QWidget):
    #Displays animated Loadscreen on Startup
    def __init__(self, videoPath, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        
        self.setWindowTitle("Loading...")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        #Video Setup
        self.videoWidget = QVideoWidget()
        layout.addWidget(self.videoWidget)
        self.setLayout(layout)
        
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.videoWidget)
        
        #Get video File
        self.player.setSource(QUrl.fromLocalFile(videoPath))
        
        self.player.mediaStatusChanged.connect(self.handleMediaStatus)
        self.player.errorOccurred.connect(self.handleError)
        
        self.player.setLoops(QMediaPlayer.Loops.Infinite)
        
        self.resize(800, 600)
        
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        self.setWindowOpacity(0.0)
        
    # Change size of Loading video    
    def handleMediaStatus(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            screen = QApplication.primaryScreen().geometry()
            
            maxWidth = int(screen.width() * 0.8)
            maxHeight = int(screen.height() * 0.8)

            #Scale vid to 80% while keeping Aspect ratio
            vidAspect = 2550 / 3300
            
            if maxHeight * vidAspect <= maxWidth:
                newHeight = maxHeight
                newWidth = int(newHeight * vidAspect)
            else:
                newWidth = maxWidth
                newHeight = int(newWidth / vidAspect)
            
            self.resize(newWidth, newHeight)
            
            self.move(
                (screen.width() - self.width()) // 2,
                (screen.height() - self.height()) // 2
            )
            
            self.fadeIn()
            self.player.play()
            
            # Artificial Timer for Presentation effect
            QTimer.singleShot(7000, self.fadeOut)
        
    #If media isn't found
    def handleError(self, error):
        print(f"Media error: {error}")
        print(f"Error string: {self.player.errorString()}")
        self.showMainWindow()
    
    # Fade in Load Screen
    def fadeIn(self):
        self.fadeAnimation = QPropertyAnimation(self, b"windowOpacity")
        self.fadeAnimation.setDuration(1000)
        self.fadeAnimation.setStartValue(0.0)
        self.fadeAnimation.setEndValue(1.0)
        self.fadeAnimation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fadeAnimation.start()
    
    # Fade out Load Screen after Artificial Timer
    def fadeOut(self):
        self.fadeAnimation = QPropertyAnimation(self, b"windowOpacity")
        self.fadeAnimation.setDuration(1000)
        self.fadeAnimation.setStartValue(1.0)
        self.fadeAnimation.setEndValue(0.0)
        self.fadeAnimation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fadeAnimation.finished.connect(self.showMainWindow)
        self.fadeAnimation.start()
    
    def showMainWindow(self):
        self.mainWindow.show()
        self.close()


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.filePath = None
        self.convertedFileData = None
        self.videoInfo = None
        self.selectedResolution = "original"
        
        # App Layout
        self.setWindowTitle("Image, Document, and Video File Converter")
        self.setMinimumSize(650, 600)

        # Create main widget and layout
        mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(10)

        # Create scroll area
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(mainWidget)
        scrollArea.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        # Set scroll area as main layout
        containerLayout = QVBoxLayout()
        containerLayout.setContentsMargins(0, 0, 0, 0)
        containerLayout.addWidget(scrollArea)
        self.setLayout(containerLayout)
        
        mainWidget.setLayout(self.mainLayout)

        title = QLabel("Selkie Converter")
        title.setObjectName("MainTitle")
        title.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Choose a file, pick a format, and convert!!")
        subtitle.setObjectName("SubTitle")
        subtitle.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(subtitle)

        # File select
        self.label = QLabel("No file selected")
        self.label.setObjectName("PathLabel")
        self.mainLayout.addWidget(self.label)

        self.btnPick = QPushButton("Choose File")
        self.btnPick.clicked.connect(self.pick)
        self.mainLayout.addWidget(self.btnPick)

        # Video info section (initially hidden)
        self.videoInfoLabel = QLabel()
        self.videoInfoLabel.setObjectName("VideoInfoLabel")
        self.videoInfoLabel.hide()
        self.mainLayout.addWidget(self.videoInfoLabel)

        # Convert label
        self.labelCon = QLabel("Convert to...")
        self.labelCon.setObjectName("ConvertLabel")
        self.mainLayout.addWidget(self.labelCon)

        # File Format dropdown
        self.formatBox = QComboBox()
        self.mainLayout.addWidget(self.formatBox)

        # Resolution section (initially hidden)
        self.resolutionLabel = QLabel("Resolution:")
        self.resolutionLabel.setObjectName("ConvertLabel")
        self.resolutionLabel.hide()
        self.mainLayout.addWidget(self.resolutionLabel)

        self.resolutionBox = QComboBox()
        self.resolutionBox.currentTextChanged.connect(self.onResolutionChanged)
        self.resolutionBox.hide()
        self.mainLayout.addWidget(self.resolutionBox)

        # Convert button
        self.btnConvert = QPushButton("Convert")
        self.btnConvert.clicked.connect(self.convert)
        self.btnConvert.setEnabled(False)
        self.mainLayout.addWidget(self.btnConvert)

        # Initially hidden email selection
        self.createEmailSelection()

        # Divider line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.mainLayout.addWidget(line)

        # Instructions title
        instructionsTitle = QLabel("Setup Instructions (READ FIRST):")
        instructionsTitle.setObjectName("InstructionsTitle")
        self.mainLayout.addWidget(instructionsTitle)

        # Instructions txt box
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setMaximumHeight(250)
        instructions.setObjectName("InstructionsBox")
        instructions.setHtml("""
        <p><b>Prerequisites:</b></p>
        <ul>
            <li>Copy Sandbox Token: jbhQRLOaLhH2RxyLv0SOchX65KKu0t2x </li>
            <li>Open Virtual machine </li>
            <li>Install flask-mail: <code>pip install flask-mail</code></li>
            <li>Install FFmpeg for video conversion</li>
        </ul>

        <p><b>Windows:</b></p>
        <ul>
            <li>In Command Prompt run: <code>set CONVERTAPI_SECRET=(your_sandbox_token_here)</code></li>
            <li>Then run <code>python cst205app.py</code> in the same window</li>
            <li>Run <code>python cst205gui.py</code> in a separate window</li>
        </ul>
        
        <p><b>Mac/Linux:</b></p>
        <ul>
            <li>In Terminal run: <code>export CONVERTAPI_SECRET=(your_sandbox_token_here)</code></li>
            <li>Then run <code>python3 cst205app.py</code> in the same window</li>
            <li>Run <code>python3 cst205gui.py</code> in a separate window</li>
        </ul>
        
        <p><b>Supported Conversions:</b></p>
        <ul>
            <li><b>Images:</b> PNG, JPG, GIF, BMP, ICO, WEBP </li>
            <li><b>Documents:</b> PDF, DOCX, DOC, TXT, HTML </li>
            <li><b>Videos:</b> MP4, MOV, AVI, MKV, WEBM, WMV (with resolution options)</li>
        </ul>
        """)

        self.mainLayout.addWidget(instructions)

        # Conversion map source for possible file extensions
        # depending on inputted file type

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

            # Videos
            '.mp4': ['mov', 'avi', 'mkv', 'webm', 'wmv'],
            '.mov': ['mp4', 'avi', 'mkv', 'webm', 'wmv'],
            '.avi': ['mp4', 'mov', 'mkv', 'webm', 'wmv'],
            '.mkv': ['mp4', 'mov', 'avi', 'webm', 'wmv'],
            '.webm': ['mp4', 'mov', 'avi', 'mkv', 'wmv'],
            '.wmv': ['mp4', 'mov', 'avi', 'mkv', 'webm']
        }

        self.videoFormats = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.wmv']

        # Apply styling
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #7ee3f7, stop:1 #4ac1f7);
                font-family: Arial, sans-serif;
                font-size: 11pt;
            }
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #1a1a1a;
                background-color: transparent;
                padding: 10px;
                selection-background-color: transparent;
                selection-color: #1a1a1a;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                padding: 8px 16px;
            }
            #MainTitle {
                font-size: 64pt;
                font-weight: bold;
                color: #1a5c7a;
                background: transparent;
                padding: 10px;
                font-family: "Nexa Round_Trial", "Arial Black", sans-serif;
            }
            #SubTitle {
                font-size: 24pt;
                font-weight: bold;
                color: white;
                background: transparent;
                padding: 3px;
            }

            #PathLabel {
                color: #1a1a1a;
                padding: 10px;
                background-color: white;
                border: 2px solid #1a5c7a;
                border-radius: 6px;
            }

            #VideoInfoLabel {
                color: #1a1a1a;
                padding: 10px;
                background-color: #e8f4f8;
                border: 2px solid #1a5c7a;
                border-radius: 6px;
                font-weight: bold;
            }

            #ConvertLabel {
                font-weight: bold;
                color: #1a5c7a;
                font-size: 12pt;
                background: transparent;
                margin-top: 10px;
            }
            #EmailTitle {
                font-size: 14pt;
                font-weight: bold;
                color: #1a5c7a;
                background: transparent;
                margin-top: 5px;
            }
            #EmailLabel {
                font-weight: bold;
                color: #1a5c7a;
                font-size: 10pt;
                background: transparent;
                margin-top: 5px;
            }
            #EmailInput, #MessageInput {
                background-color: white;
                border: 2px solid #1a5c7a;
                border-radius: 6px;
                padding: 8px;
                color: #1a1a1a;
            }
            #EmailInput:focus, #MessageInput:focus {
                border: 3px solid #ffd700;
            }
            #InstructionsTitle {
                font-size: 14pt;
                font-weight: bold;
                color: #1a5c7a;
                background: transparent;
                margin-top: 10px;
            }
            #InstructionsBox {
                background-color: white;
                border: 3px solid #1a5c7a;
                border-radius: 6px;
                padding: 10px;
                color: #1a1a1a;
            }
            QPushButton {
                padding: 10px 20px;
                background-color: #ffd700;
                color: #1a5c7a;
                border: 3px solid #1a5c7a;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover:!disabled {
                background-color: #1a5c7a;
                color: #ffd700;
                border: 3px solid #ffd700;
            }
            QPushButton:disabled {
                background-color: #b0b0b0;
                color: #5a5a5a;
                border: 2px solid #808080;
            }
            #EmailButton {
                background-color: #ff6b6b;
                color: white;
                border: 3px solid #1a5c7a;
            }
            #EmailButton:hover:!disabled {
                background-color: #1a5c7a;
                color: #ff6b6b;
                border: 3px solid #ff6b6b;
            }
            QComboBox {
                padding: 8px 12px;
                background-color: white;
                color: #1a5c7a;
                border: 2px solid #1a5c7a;
                border-radius: 4px;
                font-size: 11pt;
            }
            QComboBox:hover {
                border: 3px solid #ffd700;
                background-color: #fffef0;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #1a5c7a;
                selection-background-color: #ffd700;
                selection-color: #1a5c7a;
            }
            QFrame {
                background-color: rgba(26, 92, 122, 0.5);
            }
        """)

    def createEmailSelection(self):
        # Email divider
        self.emailDivider = QFrame()
        self.emailDivider.setFrameShape(QFrame.HLine)
        self.emailDivider.setFrameShadow(QFrame.Sunken)
        self.emailDivider.hide()
        self.mainLayout.addWidget(self.emailDivider)

        # Email title
        self.emailTitle = QLabel("📧 Email Options")
        self.emailTitle.setObjectName("EmailTitle")
        self.emailTitle.hide()
        self.mainLayout.addWidget(self.emailTitle)

        # Save/Email label
        self.saveEmailLabel = QLabel("Save the file or send it via email:")
        self.saveEmailLabel.setObjectName("EmailLabel")
        self.saveEmailLabel.hide()
        self.mainLayout.addWidget(self.saveEmailLabel)

        # Button container
        self.buttonContainer = QWidget()
        self.buttonContainer.setStyleSheet("background: transparent;")
        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(0, 0, 0, 0)
        
        # Save button
        self.btnSave = QPushButton("Save File")
        self.btnSave.clicked.connect(self.saveConvertedFile)
        self.btnSave.hide()
        buttonLayout.addWidget(self.btnSave)
        
        self.buttonContainer.setLayout(buttonLayout)
        self.buttonContainer.hide()
        self.mainLayout.addWidget(self.buttonContainer)

        # Email input
        self.emailLabel = QLabel("Recipient Email:")
        self.emailLabel.setObjectName("EmailLabel")
        self.emailLabel.hide()
        self.mainLayout.addWidget(self.emailLabel)

        self.emailInput = QLineEdit()
        self.emailInput.setPlaceholderText("Enter email address")
        self.emailInput.setObjectName("EmailInput")
        self.emailInput.hide()
        self.mainLayout.addWidget(self.emailInput)

        # Msg input
        self.messageLabel = QLabel("Email Message:")
        self.messageLabel.setObjectName("EmailLabel")
        self.messageLabel.hide()
        self.mainLayout.addWidget(self.messageLabel)

        self.messageInput = QTextEdit()
        self.messageInput.setPlaceholderText("Enter a message for the email (optional)")
        self.messageInput.setObjectName("MessageInput")
        self.messageInput.setMaximumHeight(80)
        self.messageInput.hide()
        self.mainLayout.addWidget(self.messageInput)

        # Send email button
        self.btnSendEmail = QPushButton("Send via Email")
        self.btnSendEmail.clicked.connect(self.sendEmail)
        self.btnSendEmail.setObjectName("EmailButton")
        self.btnSendEmail.hide()
        self.mainLayout.addWidget(self.btnSendEmail)

    def showEmailSection(self):
        #Show Email after Succesful Conversion
        self.emailDivider.show()
        self.emailTitle.show()
        self.saveEmailLabel.show()
        self.buttonContainer.show()
        self.btnSave.show()
        self.emailLabel.show()
        self.emailInput.show()
        self.messageLabel.show()
        self.messageInput.show()
        self.btnSendEmail.show()
        

    def hideEmailSelection(self):
        #Hide Email before succesful Conversion
        self.emailDivider.hide()
        self.emailTitle.hide()
        self.saveEmailLabel.hide()
        self.buttonContainer.hide()
        self.btnSave.hide()
        self.emailLabel.hide()
        self.emailInput.hide()
        self.messageLabel.hide()
        self.messageInput.hide()
        self.btnSendEmail.hide()

    # Checks if File is a Video
    def isVideoFile(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        return ext in self.videoFormats

    def onResolutionChanged(self, resolution):
       #Handles resolution Change
        self.selectedResolution = resolution

    def pick(self):
        #Picks a file from File system
        path, _ = QFileDialog.getOpenFileName(self, "Pick a file")
        if path:
            self.filePath = path
            filename = os.path.basename(path)
            self.label.setText(f"Selected: {filename}")
            self.convertedFileData = None
            self.videoInfo = None
            self.selectedResolution = "original"
            
            # Hide email and video sections
            self.hideEmailSelection()
            self.videoInfoLabel.hide()
            self.resolutionLabel.hide()
            self.resolutionBox.hide()

            fileExt = os.path.splitext(path)[1].lower()

            self.formatBox.clear()
            if fileExt in self.conversionMap:
                self.formatBox.addItems(self.conversionMap[fileExt])
                self.btnConvert.setEnabled(True)
                
                # If video file, get video info
                if self.isVideoFile(path):
                    self.label.setText(f"Selected: {filename} - Getting video info...")
                    QApplication.processEvents()
                    
                    videoInfo = self.getVideoInfo(path)
                    if videoInfo and 'width' in videoInfo and 'height' in videoInfo:
                        self.videoInfo = videoInfo
                        infoText = f"📹 Video Resolution: {videoInfo['width']} x {videoInfo['height']} ({videoInfo['height']}p)"
                        self.videoInfoLabel.setText(infoText)
                        self.videoInfoLabel.show()
                        
                        # Show resolution options
                        self.resolutionLabel.show()
                        self.resolutionBox.show()
                        self.resolutionBox.clear()
                        self.resolutionBox.addItems(videoInfo.get('allowed_resolutions', ['original']))
                        self.selectedResolution = "original"
                        
                    self.label.setText(f"Selected: {filename}")
            else:
                self.formatBox.addItem("No Conversion Available")
                self.btnConvert.setEnabled(False)

    def saveConvertedFile(self):
        """Save converted file to disk"""
        if not self.convertedFileData:
            QMessageBox.warning(self, "No File", "No converted file available to save.")
            return
            
        savePath, _ = QFileDialog.getSaveFileName(
            self, "Save Converted File", self.convertedFilename
        )
        if savePath:
            with open(savePath, 'wb') as out:
                out.write(self.convertedFileData)
            self.label.setText(f"✓ Saved: {os.path.basename(savePath)}")
            QMessageBox.information(self, "Success", f"File saved successfully!\n\n{savePath}")
        else:
            self.label.setText("Save canceled.")

    # Gets Video Info
    # Fix for getVideoInfo method (around line 395)
    def getVideoInfo(self, filepath):
        url = "http://127.0.0.1:5000/video-info"
        
        try:
            with open(filepath, 'rb') as f:
                files = {'file': f}
                resp = requests.post(url, files=files, timeout=30)
                status_code = resp.status_code  # ADD THIS LINE
                
            if status_code == 200:
                return resp.json()
            else:
                return None
                
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None


    # Fix for convert method (around line 450)
    def convert(self):
        if not self.filePath:
            self.label.setText("No file selected.")
            return

        url = "http://127.0.0.1:5000/convert"
        target = self.formatBox.currentText()

        try:
            with open(self.filePath, 'rb') as f:
                files = {'file': f}
                data = {'target': target, 'targetExt': target}
                
                # Add resolution for video files
                if self.isVideoFile(self.filePath):
                    data['resolution'] = self.selectedResolution
                
                self.label.setText("Converting... Please wait.")
                QApplication.processEvents()
                
                resp = requests.post(url, files=files, data=data, timeout=120)
                status_code = resp.status_code  # ADD THIS LINE
                
        except requests.exceptions.ConnectionError:
            self.label.setText("❌ Backend server not running!")
            QMessageBox.critical(self, "Backend Not Running", 
                            "Could not connect to the backend server.\n\n"
                            "Please make sure:\n"
                            "1. cst205app.py is running\n"
                            "2. The server started successfully on http://127.0.0.1:5000\n\n"
                            "Start the backend with:\n"
                            "   python cst205app.py")
            return
            
        except requests.exceptions.Timeout:
            self.label.setText("❌ Request timed out!")
            QMessageBox.critical(self, "Timeout Error", 
                            "The conversion request timed out.\n\n"
                            "The backend may be processing a large file or experiencing issues.")
            return

        except requests.exceptions.RequestException as e:
            self.label.setText(f"Error: {e}")
            QMessageBox.critical(self, "Connection Error", 
                            f"Could not connect to backend server.\n\n{e}")
            return

        if status_code == 500:
            # Backend error, likely API key issue
            self.label.setText("❌ Conversion failed - Check API key!")
            errorMsg = "Conversion failed on the backend.\n\n"
            errorMsg += "Common causes:\n"
            errorMsg += "1. ConvertAPI token not set or invalid\n"
            errorMsg += "2. ConvertAPI token expired or out of credits\n"
            errorMsg += "3. FFmpeg not installed (for video conversion)\n\n"
            errorMsg += "Make sure to set the environment variable:\n"
            errorMsg += "Windows: set CONVERTAPI_SECRET=your_token\n"
            errorMsg += "Mac/Linux: export CONVERTAPI_SECRET=your_token\n\n"
            errorMsg += "Check the backend terminal for detailed error messages."
            QMessageBox.critical(self, "Backend Error", errorMsg)
            return

        elif status_code == 200:
            # Store converted file in memory for user use
            self.convertedFileData = resp.content
            
            # Generate proper filename with original name
            originalName = os.path.splitext(os.path.basename(self.filePath))[0]
            self.convertedFilename = f"{originalName}_conv.{target}"
            
            resolutionTxt = ""
            if self.isVideoFile(self.filePath) and self.selectedResolution != "original":
                resolutionTxt = f" at {self.selectedResolution}"
            
            self.label.setText(f"✓ File converted to {target}{resolutionTxt}! Save or email below:")
            
            # Show email section
            self.showEmailSection()
            
        elif status_code == 400:
            errorTxt = resp.text
            self.label.setText("❌ Conversion failed")
            QMessageBox.warning(self, "Invalid Request", 
                            f"The file or target format may be invalid.\n\n{errorTxt}")
        else:
            self.label.setText(f"❌ Conversion failed (Status: {status_code})")
            QMessageBox.critical(self, "Conversion Error", 
                            f"File conversion failed.\n\n"
                            f"Status code: {status_code}\n"
                            f"Check backend logs for details.")


    # Fix for sendEmail method (around line 580)
    def sendEmail(self):
        if not self.convertedFileData:
            QMessageBox.warning(self, "No File", "Please convert a file first before sending via email.")
            return
        
        recipientEmail = self.emailInput.text().strip()
        
        if not recipientEmail:
            QMessageBox.warning(self, "Missing Email", 
                            "Please enter a recipient email address.")
            return
        
        # Email validation
        if '@' not in recipientEmail or '.' not in recipientEmail:
            QMessageBox.warning(self, "Invalid Email", 
                            "Please enter a valid email address.")
            return
        
        messageText = self.messageInput.toPlainText().strip()
        if not messageText:
            messageText = f"Here is your converted file: {self.convertedFilename}"
        
        url = "http://127.0.0.1:5000/send"
        
        try:
            files = {
                'file': (self.convertedFilename, self.convertedFileData, 'application/octet-stream')
            }
            data = {
                'receiverEmail': recipientEmail,
                'messages': messageText
            }
            
            self.label.setText("Sending email...")
            QApplication.processEvents()
            
            resp = requests.post(url, files=files, data=data, timeout=30)
            status_code = resp.status_code  # ADD THIS LINE
            
            if status_code == 200:
                self.label.setText(f"✓ Email sent successfully to {recipientEmail}!")
                QMessageBox.information(self, "Email Sent", 
                                    f"Your file has been sent to:\n{recipientEmail}")
                self.emailInput.clear()
                self.messageInput.clear()
            else:
                self.label.setText("Failed to send email")
                QMessageBox.critical(self, "Email Error", 
                                f"Failed to send email.\n\nStatus: {status_code}\n\n"
                                f"Possible causes:\n"
                                f"- Email credentials not configured in config.py\n"
                                f"- flask-mail not installed (pip install flask-mail)\n"
                                f"- Invalid email server settings")
        
        
        except requests.exceptions.ConnectionError:
            self.label.setText("❌ Backend server not running!")
            QMessageBox.critical(self, "Backend Not Running", 
                            "Could not connect to the backend server.\n\n"
                            "Please make sure cst205app.py is running.")

        except requests.exceptions.Timeout:
            self.label.setText("❌ Email request timed out!")
            QMessageBox.critical(self, "Timeout Error", 
                            "The email request timed out.\n\n"
                            "The email server may be slow or unavailable.")

        except requests.exceptions.RequestException as e:
            self.label.setText(f"Email error: {e}")
            QMessageBox.critical(self, "Connection Error", 
                            f"Could not connect to email server.\n\n{e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    fontID = QFontDatabase.addApplicationFont('/Users/simpcervantes/cst205/Proj/Fonts/nexaround-trial-glow.otf')
    
    mainWindow = App()
    splash = SplashScreen('icons/SelkieSplashwBkg.mp4', mainWindow)
    splash.show()
    
    sys.exit(app.exec())

