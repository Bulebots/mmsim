import struct
from itertools import product

import numpy
from pyqtgraph import GraphicsObject
from pyqtgraph import QtCore
from pyqtgraph import QtGui
from pyqtgraph import mkBrush
from pyqtgraph import mkPen

from .mazes import EAST_BIT
from .mazes import MAZE_SIZE
from .mazes import NORTH_BIT
from .mazes import SOUTH_BIT
from .mazes import VISITED_BIT
from .mazes import WEST_BIT
from .mazes import read_walls

CELL_WIDTH = 180
WALL_WIDTH = 12

GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)


def paint_walls(painter, walls, color):
    painter.setBrush(mkBrush(color))
    painter.setPen(mkPen(None))
    for (x, y) in product(range(MAZE_SIZE), repeat=2):
        wall = walls[y][x]
        if wall & EAST_BIT:
            painter.drawRect(
                QtCore.QRectF(
                    (y + 1) * CELL_WIDTH - WALL_WIDTH / 2,
                    -(x + 1) * CELL_WIDTH + WALL_WIDTH / 2,
                    WALL_WIDTH,
                    CELL_WIDTH,
                )
            )
        if wall & SOUTH_BIT:
            painter.drawRect(
                QtCore.QRectF(
                    y * CELL_WIDTH + WALL_WIDTH / 2,
                    -x * CELL_WIDTH + WALL_WIDTH / 2,
                    CELL_WIDTH,
                    WALL_WIDTH,
                )
            )
        if wall & WEST_BIT:
            painter.drawRect(
                QtCore.QRectF(
                    y * CELL_WIDTH - WALL_WIDTH / 2,
                    -(x + 1) * CELL_WIDTH + WALL_WIDTH / 2,
                    WALL_WIDTH,
                    CELL_WIDTH,
                )
            )
        if wall & NORTH_BIT:
            painter.drawRect(
                QtCore.QRectF(
                    y * CELL_WIDTH + WALL_WIDTH / 2,
                    -(x + 1) * CELL_WIDTH + WALL_WIDTH / 2,
                    CELL_WIDTH,
                    WALL_WIDTH,
                )
            )


def paint_discovered(painter, distances, walls):
    if walls is not None:
        paint_walls(painter, walls, color=WHITE)
    for (x, y) in product(range(MAZE_SIZE), repeat=2):
        painter.setPen(mkPen(color=GRAY))
        if walls is not None:
            wall = walls[x][y]
            if wall & VISITED_BIT:
                painter.setPen(mkPen(color=GREEN))
        painter.drawText(
            QtCore.QRectF(
                (x + 0.5) * CELL_WIDTH + WALL_WIDTH / 2 - 50,
                -(y + 0.5) * CELL_WIDTH + WALL_WIDTH / 2 - 50,
                100,
                100,
            ),
            QtCore.Qt.AlignCenter,
            '%s' % distances[x][y],
        )


def paint_template(painter, walls):
    if walls is not None:
        paint_walls(painter=painter, walls=walls, color=GRAY)
    for (x, y) in product(range(MAZE_SIZE + 1), repeat=2):
        painter.setBrush(mkBrush(WHITE))
        painter.setPen(mkPen(None))
        painter.drawRect(
            QtCore.QRectF(
                x * CELL_WIDTH - WALL_WIDTH / 2,
                -y * CELL_WIDTH + WALL_WIDTH / 2,
                WALL_WIDTH,
                WALL_WIDTH,
            )
        )


def paint_position(painter, x, y, direction):
    painter.setBrush(mkBrush(RED))
    painter.setPen(mkPen(None))
    if direction in ['E', 'W']:
        robot_width = 50
        robot_height = 100
    else:
        robot_width = 100
        robot_height = 50
    x_compensation = 0
    y_compensation = 0
    if direction == 'E':
        y_compensation = robot_height / 2
    elif direction == 'S':
        x_compensation = (CELL_WIDTH - robot_width) / 2
    elif direction == 'W':
        x_compensation = CELL_WIDTH - robot_width
        y_compensation = robot_height / 2
    elif direction == 'N':
        x_compensation = (CELL_WIDTH - robot_width) / 2
        y_compensation = CELL_WIDTH - robot_height
    painter.drawRect(
        QtCore.QRectF(
            x * CELL_WIDTH + x_compensation,
            -(y + 1) * CELL_WIDTH + y_compensation,
            robot_width,
            robot_height,
        )
    )


class MazeItem(GraphicsObject):
    def __init__(self):
        super().__init__()
        self.reset(None)

    def reset(self, template):
        self.distances = None
        self.walls = None
        self.template = template
        self.x = 0
        self.y = 0
        self.direction = 0

        self.picture = QtGui.QPicture()
        self.position_picture = QtGui.QPicture()

        self.generateTemplate()
        self.update()

    def generateTemplate(self):
        self.template_picture = QtGui.QPicture()
        painter = QtGui.QPainter(self.template_picture)
        painter.scale(1, -1)
        paint_template(painter=painter, walls=self.template)
        painter.end()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        painter = QtGui.QPainter(self.picture)
        painter.setFont(QtGui.QFont('times', 50))
        painter.scale(1, -1)
        paint_discovered(painter, distances=self.distances, walls=self.walls)
        painter.end()

    def generatePosition(self):
        self.position_picture = QtGui.QPicture()
        painter = QtGui.QPainter(self.position_picture)
        painter.scale(1, -1)
        paint_position(painter, x=self.x, y=self.y, direction=self.direction)
        painter.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.template_picture)
        p.drawPicture(0, 0, self.position_picture)
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.template_picture.boundingRect())

    def update_position(self, position):
        self.x, self.y, self.direction = struct.unpack('3B', position)
        self.direction = chr(self.direction)
        self.generatePosition()
        self.update()
        return read_walls(self.template, self.x, self.y, self.direction)

    def read_position_walls(self, position):
        x, y, direction = struct.unpack('3B', position)
        return read_walls(self.template, x, y, chr(direction))

    def update_discovery(self, discovery):
        order = chr(discovery[0])
        distances = discovery[1:257]
        distances = numpy.frombuffer(distances, dtype='uint8')
        distances = distances.reshape(MAZE_SIZE, MAZE_SIZE).T
        if order == 'F':
            distances = distances.T

        order = chr(discovery[257])
        walls = discovery[258:]
        walls = numpy.frombuffer(walls, dtype='uint8')
        walls = walls.reshape(MAZE_SIZE, MAZE_SIZE).T
        if order == 'F':
            walls = walls.T

        self.walls = walls
        self.distances = distances
        self.generatePicture()
        self.update()
