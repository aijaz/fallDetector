import sys
import random
import matplotlib
matplotlib.use('Qt5Agg')

from PySide6 import QtCore, QtWidgets, QtWebSockets


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from websockets.server import serve

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.setCentralWidget(self.canvas)

        n_data = 500
        self.xdata = list(range(n_data))
        self.ydata = [2 for i in range(n_data)]
        self.ydata2 = [-2 for i in range(n_data)]
        self.ydata3 = [0 for i in range(n_data)]

        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        self._plot_ref1 = None
        self._plot_ref2 = None
        self._plot_ref3 = None
        self.update_plot()

        self.show()

        # Setup a timer to trigger the redraw by calling update_plot.
        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(20)
        # self.timer.timeout.connect(self.update_plot)
        # self.timer.start()

        self.server = QtWebSockets.QWebSocketServer("", QtWebSockets.QWebSocketServer.NonSecureMode)
        self.server.listen(port=8765)
        self.server.newConnection.connect(self.onNewConnection)

        self.clientConnection = None
        self.clients = []
        self.message_num = 0

        print(self.server.isListening())

    def onNewConnection(self):
        self.clientConnection = self.server.nextPendingConnection()
        self.clientConnection.textMessageReceived.connect(self.processTextMessage)
        self.clientConnection.disconnected.connect(self.socketDisconnected)
        self.clients.append(self.clientConnection)

    def processTextMessage(self,  message):
        pitch,roll,yaw,gx,gy,gz,ax,ay,az,rx,ry,rz = message.split(",")
        self.ydata = self.ydata[1:] +   [float(ax)]
        self.ydata2 = self.ydata2[1:] + [float(ay)]
        self.ydata3 = self.ydata2[1:] + [float(az)]
        self.message_num += 1

        if self.message_num % 20 == 0:
            self.update_plot()
        # if (self.clientConnection):
        #     self.clientConnection.sendTextMessage(message)


    def socketDisconnected(self):
        if (self.clientConnection):
            self.clients.remove(self.clientConnection)
            self.clientConnection.deleteLater()


    def update_plot(self):
        # Drop off the first y element, append a new one.

        # Note: we no longer need to clear the axis.
        if self._plot_ref1 is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs1 = self.canvas.axes.plot(self.xdata, self.ydata, color='blue', label="X")
            plot_refs2 = self.canvas.axes.plot(self.xdata, self.ydata2, color='red', label="Y")
            plot_refs3 = self.canvas.axes.plot(self.xdata, self.ydata3, color='green', label="Z")
            self.canvas.axes.legend(loc="upper left")

            self._plot_ref1 = plot_refs1[0]
            self._plot_ref2 = plot_refs2[0]
            self._plot_ref3 = plot_refs3[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref1.set_ydata(self.ydata)
            self._plot_ref2.set_ydata(self.ydata2)
            self._plot_ref3.set_ydata(self.ydata3)

        # Trigger the canvas to update and redraw.
        self.canvas.draw()


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()

