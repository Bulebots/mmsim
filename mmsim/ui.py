from pathlib import Path
import sys
import zmq

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QSlider
from pyqtgraph import GraphicsLayoutWidget

from mazes import load_maze
from graphics import MazeItem


class ZMQListener(QtCore.QObject):

    message = QtCore.pyqtSignal(bytes)

    def __init__(self, context):
        super().__init__()

        self.rep = context.socket(zmq.REP)
        self.rep.bind('tcp://127.0.0.1:6574')
        self.pull = context.socket(zmq.PULL)
        self.pull.bind('inproc://reply')

        self.poller = zmq.Poller()
        self.poller.register(self.rep, zmq.POLLIN)
        self.poller.register(self.pull, zmq.POLLIN)

        self.running = True

    def loop(self):
        while self.running:
            events = dict(self.poller.poll(10))
            if not events:
                continue
            for socket in events:
                if events[socket] != zmq.POLLIN:
                    continue
                if socket == self.rep:
                    self.message.emit(socket.recv())
                elif socket == self.pull:
                    self.rep.send(socket.recv())


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Micromouse maze simulator')
        self.resize(600, 600)

        self.history = []

        frame = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(frame)

        self.graphics = GraphicsLayoutWidget()
        viewbox = self.graphics.addViewBox()
        viewbox.setAspectLocked()
        template_file = Path('../mazes/apec_2010.txt')
        template = load_maze(template_file)
        self.maze = MazeItem(template=template)
        viewbox.addItem(self.maze)

        self.label = QtWidgets.QLabel()

        self.slider = QSlider(QtCore.Qt.Horizontal)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(10)
        self.slider.setTickPosition(QSlider.TicksAbove)
        self.slider.valueChanged.connect(self.slider_value_changed)
        self.slider_update()
        self.label.setText('Ready')

        layout.addWidget(self.graphics)
        layout.addWidget(self.slider)
        layout.addWidget(self.label)

        self.setCentralWidget(frame)

        self.context = zmq.Context()
        self.reply = self.context.socket(zmq.PUSH)
        self.reply.connect('inproc://reply')

        self.thread = QtCore.QThread()
        self.zeromq_listener = ZMQListener(self.context)
        self.zeromq_listener.moveToThread(self.thread)

        self.thread.started.connect(self.zeromq_listener.loop)
        self.zeromq_listener.message.connect(self.signal_received)

        QtCore.QTimer.singleShot(0, self.thread.start)

    def slider_update(self):
        self.slider.setTickInterval(len(self.history) / 10)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.history) - 1)
        self.label_set_slider(self.slider.value())

    def slider_value_changed(self, value):
        self.label_set_slider(value)

    def label_set_slider(self, value):
        self.label.setText('{}/{}'.format(value, len(self.history) - 1))

    def signal_received(self, message):
        self.history.append(message)
        self.slider_update()
        self.reply.send(b'received!')

    def closeEvent(self, event):
        self.zeromq_listener.running = False
        self.thread.quit()
        self.thread.wait()


def run():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
