import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMainWindow,  QFrame, QLabel,  QFileDialog, QSlider
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QUrl, QThread
from PyQt5.QtGui import QPixmap,  QRegion, QPainterPath
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QSoundEffect
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.Qt import QMouseEvent
import time
import extract_audio as ea
import speech_to_text as stt

end = False

censor_pressed = False
violence_timeframes = []
beeping_timeframes = []
mute_timeframes = []
emitted = False
video_path = ""
r1 = False

class CensorThread(QThread):

    def run(self):
        global violence_timeframes
        global beeping_timeframes
        global mute_timeframes
        global video_path
        global r1

        time.sleep(1)
        while not end:
            if censor_pressed:
                if not r1:
                    r1 = True
                    print("censoring video...")
                    # video model code here
                    print("censoring video done")
                    beeping_timeframes = [(0,3), (16, 18)]
                    violence_timeframes = [(10, 14), (20, 25), (50, 55)]
                    mute_timeframes = list(set(beeping_timeframes) | set(violence_timeframes))
                
current = 0
current2 = 0
current3 = 0

prev_video_path = ""

class audiothread(QThread):
    global censor_pressed
    global video_path
    global end

    def run(self):
        censored = False
        while not end:
            if censor_pressed:
                if not censored:
                    censored = True
                    print("censoring audio....")
                    audio_file = ea.extract_aduio(video_path)
                    text = stt.speech_to_text(audio_file)
                    # audio model code here
                    print("censoring audio done")

class frame_hide_thread(QThread):
    update_signal = pyqtSignal(int)

    def run(self):
        global current
        global window
        global censor_pressed
        time.sleep(1)
        prev = current
        while not end:
            current = window.video_app.mediaPlayer.position() // 1000
            if current != prev:
               # print("Change")
                if censor_pressed:
                    self.update_signal.emit(current)
            prev = current

class audio_beeping_thread(QThread):
    update_signal = pyqtSignal(int)

    def run(self):
        global current2
        global window
        global censor_pressed
        time.sleep(1)
        prev = current2
        while not end:
            current2 = window.video_app.mediaPlayer.position() // 1000
            if current2 != prev:
                if censor_pressed:
                    self.update_signal.emit(current2)
            prev = current2

class mute_thread(QThread):
    update_signal = pyqtSignal(int)
    
    def run(self):
        global current3
        global window
        global censor_pressed
        time.sleep(1)
        prev = current3
        while not end:
            current3 = window.video_app.mediaPlayer.position() // 1000
            if current3 != prev:
                if censor_pressed:
                    self.update_signal.emit(current3)
            prev = current3

def mute_sound():
    global current3
    global mute_timeframes
    for i in mute_timeframes:
        if current >= i[0] and current <= i[1]:
            window.video_app.mediaPlayer.setMuted(True)
        else:
            found = False
            for x in mute_timeframes:
                if current2 >= x[0] and current2 <= x[1]:
                    found = True
            if found == False:
                window.video_app.mediaPlayer.setMuted(False)

def beep_sound():
    global current2
    global beeping_timeframes
    for i in beeping_timeframes:
        if current >= i[0] and current <= i[1]:
            #window.video_app.mediaPlayer.setMuted(True)
            window.video_app.beep_sound.play()
        else:
            found = False
            for x in beeping_timeframes:
                if current2 >= x[0] and current2 <= x[1]:
                    found = True
            if found == False:
                #window.video_app.mediaPlayer.setMuted(False)
                window.video_app.beep_sound.stop()
            
def addshutter():
   # print("shutter called")
    global current
    for i in violence_timeframes:
        if current >= i[0] and current <= i[1]:
            #print("yes")
            if len(window.shutters) == 0:
                f = QLabel(window)
                f.setStyleSheet("background-color: rgba(255,0,0,1);")
                f.setGeometry(11, 59, 1000, 720)
                f.show()
                window.shutters.append(f)
                #window.video_app.mediaPlayer.setMuted(True)
        else:
            found = False
            for x in violence_timeframes:
                if current >= x[0] and current <= x[1]:
                    found = True
            if found == False:
                for i in window.shutters:
                    i.hide()
                    window.shutters = []
                    print("opening voice")
                    #window.video_app.mediaPlayer.setMuted(False)

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video Player')
        self.setGeometry(100, 100, 800, 600)

        self.videoWidget = QVideoWidget()
        self.videoWidget.setFixedSize(1000, 720)
        self.videoWidget.setStyleSheet("background-color: rgba(30,30,30,0.5);")
        self.videoWidget.setGeometry(0, 0, 1000, 720)


        self.playButton = QPushButton('Play')
        self.playButton.setFixedWidth(200)
        self.stopButton = QPushButton('Stop')
        self.stopButton.setFixedWidth(200)
        self.openButton = QPushButton('Upload')
        self.openButton.setFixedWidth(200)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setFixedWidth(1000)
        self.slider.sliderMoved.connect(self.setSliderPosition)

        self.playButton.clicked.connect(self.playVideo)
        self.stopButton.clicked.connect(self.stopVideo)
        self.openButton.clicked.connect(self.openFile)

        self.openButton.setCursor(Qt.PointingHandCursor)
        self.playButton.setCursor(Qt.PointingHandCursor)
        self.stopButton.setCursor(Qt.PointingHandCursor)


        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.stopButton)
        controlLayout.setSpacing(100)

        controlLayout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.videoWidget)
        self.layout.addWidget(self.slider)
        #self.layout.addLayout(controlLayout)
        #layout.addWidget(self.lb)

        #############################################################
        # Add volume control
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(50)
        self.volumeSlider.setFixedWidth(100)
        self.volumeSlider.valueChanged.connect(self.setVolume)

        # # Add volume control to layout
        self.layout.addWidget(self.volumeSlider)

        # # Add mute button
        # self.muteButton = QPushButton('Mute')
        # self.muteButton.setFixedWidth(100)
        # self.muteButton.clicked.connect(self.toggleMute)
        # self.layout.addWidget(self.muteButton)
        ############################################################
        self.layout.addLayout(controlLayout)  
        #self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

        # Add QLabel to display current time
        self.timeLabel = QLabel('0:00 / 0:00', self)
        self.timeLabel.setAlignment(Qt.AlignCenter)
        self.timeLabel.setStyleSheet("color: red;")

        # Add QPushButton to print current time
        # self.printTimeButton = QPushButton('Print Time', self)
        # self.printTimeButton.setFixedWidth(200)
        # self.printTimeButton.clicked.connect(self.CurrentTime)
        # self.printTimeButton.setCursor(Qt.PointingHandCursor)

        self.layout.addWidget(self.timeLabel)
        #self.layout.addWidget(self.printTimeButton)

        self.setLayout(self.layout)

        # Connect slot for updating timeLabel
        self.mediaPlayer.positionChanged.connect(self.updateTimeLabel)

        # self.shutter = QLabel(self)
        # self.shutter.setStyleSheet("background-color: rgba(255,0,0,1);")
        # self.shutter.setGeometry(11, 11, 1, 1)
        #self.shutter.setParent(None)

        self.beep_sound = QSoundEffect()
        self.beep_sound.setSource(QUrl.fromLocalFile('beep.wav'))

        style= """
        QPushButton {
            background-color: rgba(20, 20, 20, 0.5);
            border: 1px solid tomato;
            color: white;
            padding: 4px;
            margin: 0px;
            height:40px;
            }
        QPushButton:hover {
            background-color: #001121;
            font-weight: bold;
        }
          """
        self.setStyleSheet(style)

    def loop_thread(self):
        while(1):
            self.CurrentTime()
    
    def main_thread(self):        
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def playVideo(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def stopVideo(self):
        self.mediaPlayer.stop()

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie", "", "Video Files (*.mp4 *.avi *.mkv)")
        if fileName != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            global video_path
            video_path = fileName

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setText('Pause')
        else:
            self.playButton.setText('Play')

    def positionChanged(self, position):
        self.slider.setValue(position)

    def durationChanged(self, duration):
        self.slider.setRange(0, duration)

    def setSliderPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def CurrentTime(self):
        global timeframes
        current_time = self.mediaPlayer.position() // 1000
        for i in timeframes:
            if current_time >= i[0] and current_time <= i[1]:
                self.addshutter()
            else:
                found = False
                for x in timeframes:
                    if current_time >= x[0] and current_time <= x[1]:
                        found = True
                if found == False:
                    self.removeshutter()
        return current_time

    def addshutter(self):
        self.shutter.setGeometry(11, 11, 1000, 720)
    
    def removeshutter(self):
        self.shutter.setGeometry(11, 11, 1, 1)

    def updateTimeLabel(self, position):
        duration = self.mediaPlayer.duration() // 1000  # convert milliseconds to seconds
        current_time = position // 1000  # convert milliseconds to seconds

        formatted_time = f"{current_time // 60}:{current_time % 60:02d} / {duration // 60}:{duration % 60:02d}"
        self.timeLabel.setText(formatted_time)

    def setVolume(self, volume):
        self.mediaPlayer.setVolume(volume)

    def toggleMute(self):
        if self.mediaPlayer.isMuted():
            self.mediaPlayer.setMuted(False)
            #self.muteButton.setText('Mute')
        else:
            self.mediaPlayer.setMuted(True)
            #self.muteButton.setText('Unmute')

class CustomTitleBar(QWidget):
    closeSignal = pyqtSignal()
    minimizeSignal = pyqtSignal()
    maximizeSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        #self.draggable = False
        #self.offset = None

        # Create buttons
        self.close_button = QPushButton("x", self, clicked=self.emit_close_signal)
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedWidth(55)

        # Create layout
        self.layout = QHBoxLayout(self)

        self.layout.addWidget(self.close_button, 0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.layout.setObjectName("customTitleBar")
        
        self.minimize_button = QPushButton("_", self, clicked=self.emit_minimize_signal)
        self.minimize_button.setObjectName("minimizeButton")
        self.minimize_button.setFixedWidth(55)
        self.layout.addWidget(self.minimize_button, 0)

        self.maximize_button = QPushButton("+", self, clicked=self.emit_maximize_signal)
        self.maximize_button.setObjectName("maximizeButton")
        self.maximize_button.setFixedWidth(55)

# add a widget to the layout to display the logo icon.png
        self.logo = QLabel(self)
        self.logo.setPixmap(QPixmap('icon.png').scaled(40, 40, Qt.KeepAspectRatio, Qt.FastTransformation))
        self.logo.setObjectName("logo")
        self.layout.addWidget(self.logo, 0)

        separator = QFrame(self)
        separator.setObjectName("separator")
        separator.setFixedWidth(1094)

        self.layout.addWidget(separator)

        self.layout.addWidget(self.minimize_button, 0)
        self.layout.addWidget(self.maximize_button, 0)
        self.layout.addWidget(self.close_button, 0)
        
        self.layout.setSpacing(0)


        # Apply style using CSS
        style = """
            QLabel#logo {
            background-color: blue;
            margin: 0px;
            padding: 4px;
            }
            QFrame#separator {
            background-color: blue;
            height: 40px;
            }
            QPushButton#maximizeButton, QPushButton#minimizeButton {
                background-color: #0B2031;
                border: none;
                color: white;
                padding: 4px;
                margin: 0px;
                height:40px;
            }
            QPushButton#closeButton {
                background-color: tomato;
                border: none;
                color: white;
                padding: 4px;
                margin: 0px;
                height:40px;
            }
            QPushButton#closeButton:hover {
                background-color: red;
                font-weight: bold;
            }
            QPushButton#minimizeButton:hover, QPushButton#maximizeButton:hover {
                background-color: #001121;
                font-weight: bold;
            }
        """
        self.setStyleSheet(style)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.minimize_button.setCursor(Qt.PointingHandCursor)
        self.maximize_button.setCursor(Qt.PointingHandCursor)
    
    def emit_maximize_signal(self):
        self.maximizeSignal.emit()

    def emit_close_signal(self):
        self.closeSignal.emit()

    def emit_minimize_signal(self):
        self.minimizeSignal.emit()

def censorvideo():
    global prev_video_path
    global violence_timeframes
    global beeping_timeframes
    global mute_timeframes
    global video_path
    global censor_pressed
    global r1

    if video_path != "":
        if prev_video_path == "":
            prev_video_path = video_path
        elif video_path != "" and video_path != prev_video_path:
            prev_video_path = video_path
            violence_timeframes = []
            beeping_timeframes = []
            mute_timeframes = []
            r1 = False
        censor_pressed = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.shutters = []
        self.draggable = False
        self.offset = None

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(1300, 800)
        #self.setStyleSheet("background-color: #8cbfe2; color: white; margin:0;padding:0")
        self.setStyleSheet("background-color: black; color: white; margin:0;padding:0")
        # Create custom title bar
        title_bar = CustomTitleBar()
        title_bar.closeSignal.connect(self.closeall)  # Connect close signal to close the main window
        title_bar.minimizeSignal.connect(self.showMinimized)
        title_bar.maximizeSignal.connect(self.showMaximized)

        # Set central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.addWidget(title_bar)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.video_app = VideoPlayer()
        self.main_layout.addWidget(self.video_app)

        self.censor = QPushButton("Censor", self)

        style = """
        QPushButton {
            background-color: tomato;
            border: 1px solid red;
            color: white;
            padding: 4px;
            margin-top: 0px;
            }
        QPushButton:hover {
            background-color: #001121;
            font-weight: bold;
        }
        """
        self.censor.setStyleSheet(style)
        self.censor.setCursor(Qt.PointingHandCursor)
        self.censor.setGeometry(1050, 815, 200, 49)
        self.censor.clicked.connect(censorvideo)

       # main_layout.addWidget(self.censor)
        #self.censor.setAlignment(Qt.AlignCenter)

        #self.setCurvedEdges()
    
    def closeall(self):
        global end
        end = True
        self.close()

    def setCurvedEdges(self):
        rect = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(rect, 20, 20)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.draggable = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.draggable:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.draggable = False


app = QApplication(sys.argv)
window = MainWindow()
window.show()


if __name__ == "__main__":

    model_thread = CensorThread()
    model_thread.start()

    frame_thread = frame_hide_thread()
    frame_thread.update_signal.connect(addshutter)
    frame_thread.start()

    audio_thread = audio_beeping_thread()
    audio_thread.update_signal.connect(beep_sound)
    audio_thread.start()

    mute_thread = mute_thread()
    mute_thread.update_signal.connect(mute_sound)
    mute_thread.start()

    app.exec_()

    model_thread.quit()
    model_thread.wait()

    frame_thread.quit()
    frame_thread.wait()

    audio_thread.quit()
    audio_thread.wait()

    mute_thread.quit()
    mute_thread.wait()