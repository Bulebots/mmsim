import struct

import zmq

MAZE_SIZE = 16

ctx = zmq.Context()
req = ctx.socket(zmq.REQ)
req.connect('tcp://127.0.0.1:6574')


def ping():
    req.send(b'ping')
    return req.recv()


def reset():
    req.send(b'reset')
    return req.recv()


def read_walls(x, y, direction):
    direction = direction[0].upper().encode()
    req.send(b'W' + struct.pack('2B', x, y) + direction)
    return dict(
        zip(['left', 'front', 'right'], struct.unpack('3B', req.recv()))
    )


def send_state(x, y, direction, maze_weights, maze_walls):
    direction = direction[0].upper().encode()
    state = b'S' + struct.pack('2B', x, y) + direction
    state += b'F'
    for row in maze_weights:
        for weight in row:
            state += struct.pack('B', weight)
    state += b'F'
    for row in maze_walls:
        for walls in row:
            state += struct.pack('B', walls)
    req.send(state)
    return req.recv()


if __name__ == '__main__':
    # Ping request
    print('Sending ping... ')
    print('> ', ping())

    # Reset request
    print('Resetting simulation... ')
    print('> ', reset())

    # Read walls request at (0, 0) and facing north
    params = {'x': 0, 'y': 0, 'direction': 'north'}
    print('Walls at ({x}, {y}) facing {direction}... '.format(**params))
    print('> ', read_walls(**params))

    # Read walls request at (1, 0) and facing east
    params = {'x': 1, 'y': 0, 'direction': 'east'}
    print('Walls at ({x}, {y}) facing {direction}... '.format(**params))
    print('> ', read_walls(**params))

    # Send state request with no walls and all weights set to zero
    maze_walls = [[0 for y in range(MAZE_SIZE)] for x in range(MAZE_SIZE)]
    maze_weights = [[0 for y in range(MAZE_SIZE)] for x in range(MAZE_SIZE)]
    send_state(0, 0, 'north', maze_weights, maze_walls)

    # Change weights to increase in the "x" direction
    maze_weights = [[x for y in range(MAZE_SIZE)] for x in range(MAZE_SIZE)]
    send_state(0, 0, 'north', maze_weights, maze_walls)

    # Change weights to increase in the "y" direction
    maze_weights = [[y for y in range(MAZE_SIZE)] for x in range(MAZE_SIZE)]
    send_state(0, 0, 'north', maze_weights, maze_walls)

    # Changing mouse position (move north)
    send_state(0, 1, 'north', maze_weights, maze_walls)
    send_state(0, 2, 'north', maze_weights, maze_walls)
    send_state(0, 3, 'north', maze_weights, maze_walls)

    # Changing mouse position (move east)
    send_state(1, 3, 'east', maze_weights, maze_walls)
    send_state(2, 3, 'east', maze_weights, maze_walls)
    send_state(3, 3, 'east', maze_weights, maze_walls)

    # Set all cells as visited
    maze_walls = [[1 for y in range(MAZE_SIZE)] for x in range(MAZE_SIZE)]
    send_state(3, 3, 'east', maze_weights, maze_walls)

    # Set only and all East walls
    maze_walls = [[2 for y in range(MAZE_SIZE)] for x in range(MAZE_SIZE)]
    send_state(3, 3, 'east', maze_weights, maze_walls)

    # Set only and all South walls
    maze_walls = [[4 for y in range(MAZE_SIZE)] for x in range(MAZE_SIZE)]
    send_state(3, 3, 'east', maze_weights, maze_walls)

    # Set variable walls and visited bit in the "y" direction
    maze_walls = [[y for y in range(MAZE_SIZE)] for x in range(MAZE_SIZE)]
    send_state(3, 3, 'east', maze_weights, maze_walls)

    print('Use the slider in the simulator to navigate the state history!')
