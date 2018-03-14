from pathlib import Path
import struct
import sys
import zmq

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QSlider
from pyqtgraph import GraphicsLayoutWidget

from .mazes import load_maze
from .graphics import MazeItem


class ZMQListener(QtCore.QObject):

    message = QtCore.pyqtSignal(bytes)

    def __init__(self, context, host, port):
        super().__init__()

        self.rep = context.socket(zmq.REP)
        self.rep.bind('tcp://{host}:{port}'.format(host=host, port=port))
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
            self.process_events(events)

    def process_events(self, events):
        for socket in events:
            if events[socket] != zmq.POLLIN:
                continue
            if socket == self.rep:
                self.message.emit(socket.recv())
            elif socket == self.pull:
                self.rep.send(socket.recv())


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, host, port, maze, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Micromouse maze simulator')
        self.resize(600, 600)

        self.history = []

        frame = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(frame)

        self.graphics = GraphicsLayoutWidget()
        viewbox = self.graphics.addViewBox()
        viewbox.setAspectLocked()
        template_file = Path(maze)
        template = load_maze(template_file)
        self.maze = MazeItem(template=template)
        viewbox.addItem(self.maze)

        self.label = QtWidgets.QLabel()

        self.slider = QSlider(QtCore.Qt.Horizontal)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(10)
        self.slider.setTickPosition(QSlider.TicksAbove)
        self.slider.valueChanged.connect(self.slider_value_changed)
        self.reset()

        layout.addWidget(self.graphics)
        layout.addWidget(self.slider)
        layout.addWidget(self.label)

        self.setCentralWidget(frame)

        self.context = zmq.Context()
        self.reply = self.context.socket(zmq.PUSH)
        self.reply.connect('inproc://reply')

        self.thread = QtCore.QThread()
        self.zeromq_listener = ZMQListener(self.context, host=host, port=port)
        self.zeromq_listener.moveToThread(self.thread)

        self.thread.started.connect(self.zeromq_listener.loop)
        self.zeromq_listener.message.connect(self.signal_received)

        QtCore.QTimer.singleShot(0, self.thread.start)

    def reset(self):
        self.history = []
        self.slider.setValue(-1)
        self.slider.setRange(-1, -1)
        self.label.setText('Ready')

    def slider_update(self):
        self.slider.setTickInterval(len(self.history) / 10)
        self.slider.setRange(0, len(self.history) - 1)
        self.label_set_slider(self.slider.value())

    def slider_value_changed(self, value):
        self.label_set_slider(value)
        if not len(self.history):
            return
        state = self.history[value]
        position = state[:3]
        discovery = state[3:]
        self.maze.update_position(position)
        self.maze.update_discovery(discovery)

    def label_set_slider(self, value):
        self.label.setText('{}/{}'.format(value, len(self.history) - 1))

    def signal_received(self, message):
        if message.startswith(b'W'):
            walls = self.maze.read_position_walls(message.lstrip(b'W'))
            self.reply.send(struct.pack('3B', *walls))
            return
        if message.startswith(b'S'):
            message = message.lstrip(b'S')
            self.history.append(message)
            self.reply.send(b'ok')
            self.slider_update()
            return
        if message == b'RESET':
            self.reset()
            self.reply.send(b'ok')
            return
        raise ValueError('Unknown message received! "{}"'.format(message))

    def closeEvent(self, event):
        self.zeromq_listener.running = False
        self.thread.quit()
        self.thread.wait()


def run(host, port, maze):
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow(host=host, port=port, maze=maze)
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
