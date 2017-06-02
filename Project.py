import sys
from PyQt4 import QtGui, QtCore
import cv2
import datetime
now=datetime.datetime.now()
app = QtGui.QApplication(sys.argv)


class VideoCapture(QtGui.QWidget):

    a = 1
    img = []
    b=0
    c=0
    d=False
    Working = False
    forError=False


    try:
        settingsFile=open('settings.dat')
        settingsData=settingsFile.read()
        settingsFile.close()
    except:
        settingsData="ff.xml  40  C:/Users/user/Pictures/  10  2  0  0"
        file=open("settings.dat", 'w')
        file.write(settingsData)

    settingsData = settingsData.split("  ")
    classDir=settingsData[0]
    fps = int(settingsData[1])
    fsd = settingsData[2]
    time_ = int(settingsData[3])
    lack_ = int(settingsData[4])
    time = time_*fps
    lack = lack_*fps
    dateORnumber = int(settingsData[5])
    numCam=int(settingsData[6])
    try:
        fileClass=open(classDir)
        fileClass.close()
    except:
        classDir = QtGui.QFileDialog.getOpenFileName(None,'Open classifier', '\\')
        file = open("settings.dat", "w")
        data = str(classDir) + "  " + str(fps) + "  " + str(fsd) + "  " + str(time_) + "  " + str(lack_) + "  " + str(dateORnumber+"  "+ str(numCam))
        file.write(data)
    classifier = cv2.CascadeClassifier(str(classDir))

    #ff.xml  40  C:/Users/user/Pictures/  10  2  0  0

    def __init__(self, parent):
        super(QtGui.QWidget, self).__init__()
        self.cap = cv2.VideoCapture(self.numCam)
        self.video_frame=QtGui.QLabel()
        self.layout = QtGui.QFormLayout(self)
        self.layout.addWidget(self.video_frame)
        self.setLayout(self.layout)

    def nextFrameSlot(self):
        try:
            ret, frame = self.cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if self.classifier is not None and self.Working:
                detects = self.classifier.detectMultiScale(gray, scaleFactor=1.3,
                                                           minNeighbors=4,
                                                           minSize=(30, 30),
                                                           flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
                for (x, y, w, h) in detects:
                    (e, d) = (min(x + w, 640), min(y + h, 480))
                    cv2.rectangle(frame, (x, y), (e, d), (255, 0, 0), 2)
                if not detects == ():
                    self.b += 1
                    print self.b
                    if self.time == self.b:
                        print "Saving..."
                        self.saveFace()
                    if self.b > self.time + 2:
                        self.b = self.time + 1
                    self.c = 0
                    self.d = True
                else:
                    if self.d:
                        self.c += 1
                    if self.lack == self.c:
                        if self.d:
                            print "zero!"
                            self.b = 0
                        self.d = False

            self.img = frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = QtGui.QImage(frame, frame.shape[1], frame.shape[0],
                               QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap.fromImage(img)
            self.video_frame.setPixmap(pix)
            self.forError=False
        except:
            if not self.forError:
                QtGui.QMessageBox.information(None, "Error", "Cam error! Check the camera or go to settings and restart this program")
                self.dialog = SettingsWindow()
                self.dialog.show()
                self.forError=True
            self.timer.stop()


    def start(self):
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000.0/self.fps)

    def pause(self):
        self.timer.stop()

    def deleteLater(self):
        self.cap.release()
        super(QtGui.QWidget, self).deleteLater()

    def saveFace(self):
        if self.dateORnumber==0:
            cv2.imwrite( str(self.fsd)+"_"+str(now.year)+"-"+str(now.month)+"-"+str(now.day)+"_"+str(now.hour)+":"+str(now.minute) + ".jpg", self.img)
        else:
            self.a+=1
            cv2.imwrite(str(self.fsd)+"_"+self.a+".jpg", self.img)
        print "saved!"




class ControlWindow(QtGui.QMainWindow):
    def __init__(self):
        super(ControlWindow, self).__init__()
        self.setGeometry(50,50,670,520)
        self.setWindowTitle("Mag")

        exit = QtGui.QAction('Settings', self)
        exit.setShortcut('Ctrl+s')
        exit.setStatusTip('Settings')
        self.connect(exit, QtCore.SIGNAL('triggered()'), self.setT)

        exit1 = QtGui.QAction('Start', self)
        exit1.setShortcut('Alt+s')
        exit1.setStatusTip('Start search')
        self.connect(exit1, QtCore.SIGNAL('triggered()'), self.startSearch)

        self.statusBar()
        self.setFocus()


        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(exit1)
        file.addAction(exit)
        self.vc = VideoCapture(self)

        self.setCentralWidget(self.vc)
        self.vc.start()

    def startSearch(self):
        self.vc.Working = not self.vc.Working
        if not self.vc.Working:
            print "Work is running"
        else:
            print "Work is stopped"

    def setT(self):
        if not hasattr(self, 'dialog'):
            self.dialog=SettingsWindow()
            self.dialog.show()


class SettingsWindow(QtGui.QDialog):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.setGeometry(50, 50, 750, 350)
        self.setWindowTitle("Settings")
        self.vc = VideoCapture(self)


        self.classifierButton = QtGui.QPushButton("Select classifier", self)
        self.classifierLabel = QtGui.QLabel("Currently selected: "+ str(self.vc.classDir))

        self.fileSaveDirButton = QtGui.QPushButton("Directory and name of the file to save", self)
        self.fileSaveDirLabel = QtGui.QLabel("Currently selected: " + str(self.vc.fsd))

        self.fpsLabel = QtGui.QLabel("Select FPS (recommended 40): " + str(self.vc.fps))
        self.fpsSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.fpsSlider.setMinimum(5)
        self.fpsSlider.setMaximum(60)
        self.fpsSlider.setValue(self.vc.fps)

        self.timing = QtGui.QLabel("Timer before shooting: " + str(self.vc.time_))
        self.timingSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.timingSlider.setMinimum(1)
        self.timingSlider.setMaximum(60)
        self.timingSlider.setValue(self.vc.time_)

        self.lack = QtGui.QLabel("Maximum time of human disappearance from the frame: " + str(self.vc.lack_))
        self.lackSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.lackSlider.setMinimum(0)
        self.lackSlider.setMaximum(15)
        self.lackSlider.setValue(self.vc.lack_)

        self.cam = QtGui.QLabel("Selected cam (and restart program): " + str(self.vc.numCam+1))
        self.camSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.camSlider.setMinimum(0)
        self.camSlider.setMaximum(3)
        self.camSlider.setValue(self.vc.numCam)

        if self.vc.dateORnumber==0:
            a="date and time"
            b="number"
        else:
            a="number"
            b="date and time"
        self.don = QtGui.QLabel("To the file name will be added: " + a)
        self.donButton = QtGui.QPushButton("Set "+b, self)

        self.creator = QtGui.QLabel("Creator of the program: Appolonov Georgiy (student)")

        self.saveSettingsButton = QtGui.QPushButton("Save settings", self)


        self.saveSettingsButton.clicked.connect(self.saveSettings)
        self.classifierButton.clicked.connect(self.setclassifier)
        self.fileSaveDirButton.clicked.connect(self.showOpenDialog)
        self.donButton.clicked.connect(self.dateornum)
        self.fpsSlider.valueChanged.connect(self.fps_)
        self.timingSlider.valueChanged.connect(self.time_)
        self.lackSlider.valueChanged.connect(self.lack_)
        self.camSlider.valueChanged.connect(self.camera)

        self.grid = QtGui.QGridLayout(self)
        self.setLayout(self.grid)

        self.grid.addWidget(self.classifierButton, 0, 0)
        self.grid.addWidget(self.classifierLabel, 0, 1)
        self.grid.addWidget(self.fileSaveDirButton, 1, 0)
        self.grid.addWidget(self.fileSaveDirLabel, 1, 1)
        self.grid.addWidget(self.fpsLabel, 2, 0)
        self.grid.addWidget(self.fpsSlider, 2, 1)
        self.grid.addWidget(self.timing, 3, 0)
        self.grid.addWidget(self.timingSlider, 3, 1)
        self.grid.addWidget(self.lack, 4, 0)
        self.grid.addWidget(self.lackSlider, 4, 1)
        self.grid.addWidget(self.cam, 5, 0)
        self.grid.addWidget(self.camSlider, 5, 1)
        self.grid.addWidget(self.don, 6, 0)
        self.grid.addWidget(self.donButton, 6, 1)
        self.grid.addWidget(self.creator, 7, 0)
        self.grid.addWidget(self.saveSettingsButton, 7, 1)


    def camera(self):
        self.vc.numCam=self.camSlider.value()
        self.cam.setText("Selected cam (and restart program): " + str(self.vc.numCam+1))

    def fps_(self):
        self.vc.fps=self.fpsSlider.value()
        self.fpsLabel.setText("Select FPS (recommended 40): " + str(self.vc.fps))

    def time_(self):
        self.vc.time_=self.timingSlider.value()
        self.timing.setText("Timer before shooting: " + str(self.vc.time_))

    def lack_(self):
        self.vc.lack_=self.lackSlider.value()
        self.lack.setText("Maximum time of human disappearance from the frame: " + str(self.vc.lack_))

    def dateornum(self):
        if self.vc.dateORnumber==0:
            self.vc.dateORnumber=1
            self.don.setText("To the file name will be added: " + "number")
            self.donButton.setText("Set " + "date and time")
        else:
            self.vc.dateORnumber=0
            self.don.setText("To the file name will be added: " + "date and time")
            self.donButton.setText("Set " + "number")

    def setclassifier(self):
        a = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '\\')
        if not a=="":
            self.vc.classDir = a
        self.classifierLabel.setText("Currently selected: "+self.vc.classDir)

    def saveSettings(self):
        file = open("settings.dat", "w")
        data=str(self.vc.classDir)+"  "+str(self.vc.fps)+"  "+str(self.vc.fsd)+"  "+str(self.vc.time_)+"  "+str(self.vc.lack_)+"  "+str(self.vc.dateORnumber)+"  "+ str(self.vc.numCam)
        file.write(data)

    def showOpenDialog(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save...', '\\')
        if not filename=="":
            self.vc.fsd=(str(filename))
        self.fileSaveDirLabel.setText("Currently selected: " + str(self.vc.fsd))

def main():
    window = ControlWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()




