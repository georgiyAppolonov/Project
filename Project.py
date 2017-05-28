import sys
from PyQt4 import QtGui, QtCore
import cv2


class VideoCapture(QtGui.QWidget):

    a = 1
    img = []
    classifier = cv2.CascadeClassifier('ff.xml')
    fsd='abra'
    chelovek = False

    def __init__(self, parent):
        #self.classifier = None
        super(QtGui.QWidget, self).__init__()
        self.cap = cv2.VideoCapture(0)
        self.video_frame=QtGui.QLabel()
        self.layout = QtGui.QFormLayout(self)
        self.layout.addWidget(self.video_frame)
        self.setLayout(self.layout)

    def nextFrameSlot(self):
        ret, frame = self.cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.classifier is not None:
            self.chelovek = True
            detects = self.classifier.detectMultiScale(gray, scaleFactor=1.3,
                                               minNeighbors=4,
                                               minSize=(30, 30),
                                               flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
            for (x, y, w, h) in detects:
                (e, d) = (min(x + w, 640), min(y + h, 480))
                cv2.rectangle(frame, (x, y), (e, d), (255, 0, 0), 2)

        else:
            self.chelovek = False

        self.img = frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = QtGui.QImage(frame, frame.shape[1], frame.shape[0],
                           QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)


    def start(self):
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000.0/40)

    def pause(self):
        self.timer.stop()

    def deleteLater(self):
        self.cap.release()
        super(QtGui.QWidget, self).deleteLater()

    def setFileSave(self, fsd):
        self.fsd = fsd

    def saveFace(self):
        if self.chelovek:

            cv2.imwrite( str(self.fsd)+ str(self.a) + ".jpg", self.img)
            self.a+=1
            print "saved!"



class ControlWindow(QtGui.QMainWindow):
    def __init__(self):
        super(ControlWindow, self).__init__()
        self.setGeometry(50,50,670,520)
        self.setWindowTitle("Mag")

        exit = QtGui.QAction('Save', self)
        exit.setShortcut('Ctrl+s')
        exit.setStatusTip('Save file direktory')
        self.connect(exit, QtCore.SIGNAL('triggered()'), self.showOpenDialog)
        self.statusBar()
        self.setFocus()


        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(exit)
        self.vc = VideoCapture(self)
        self.setCentralWidget(self.vc)
        self.vc.start()

    def showOpenDialog(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save...', '\\')
        self.vc.setFileSave(str(filename))
        self.vc.saveFace()

def main():
    app = QtGui.QApplication(sys.argv)
    window = ControlWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()




