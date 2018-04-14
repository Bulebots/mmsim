.. index:: protocol


********
Protocol
********


.. index:: communication

Communication
=============

The Micromouse Maze Simulator acts as a server, which means any client can
connect to it and communicate with it using message passing.

Using message passing for communication means you can use any programming
language to implement the client, as long as you correctly implement the
communication protocol.

Communication is implemented using `ØMQ <zeromq.org>`_, which is available for
almost every programming language and implements multiplatform inter-process
communication in a much more convenient way than raw TCP sockets.

To see which interface/port the server binds to by default::

   mmsim --help

Note, however, that you can specify your preferred interface/port when
launching the server::

   mmsim --host 127.0.0.1 --port 1234

The server binds a single `REP socket
<http://zguide.zeromq.org/page:all#Ask-and-Ye-Shall-Receive>`_, which means the
client is expected to communicate with the server sending requests, and the
server will always send a reply back. This is important, as you must remember
to receive and process that reply from the client. ØMQ forces the request-reply
communication pattern to be correct and complete.


.. index:: basic, client

Implementing a basic client
===========================

To better understand how this works, we will start by implementing a very
simple client in Python, to make sure the connection is well established:

.. code:: python

   import zmq


   ctx = zmq.Context()
   req = ctx.socket(zmq.REQ)
   req.connect('tcp://127.0.0.1:6574')

   req.send(b'ping')

   reply = req.recv()
   print(reply)

This simple client will send a ``ping`` request to the server and the server
will reply back with a ``pong`` message.

.. note:: If you start the client before the server, it will wait for the
   server to be available.

In C it would look like this:

.. code:: c

   #include <stdio.h>

   #include <zmq.h>


   int main (void)
   {
       char buffer[4];
       void *context = zmq_ctx_new();
       void *requester = zmq_socket(context, ZMQ_REQ);

       zmq_connect(requester, "tcp://127.0.0.1:6574");
       zmq_send(requester, "ping", 4, 0);
       zmq_recv(requester, buffer, 4, 0);
       printf("%s\n", buffer);

       zmq_close(requester);
       zmq_ctx_destroy(context);
       return 0;
   }

Which can be compiled with::

   gcc client.c -o client -lzmq

And should result in the same ``pong`` reply being printed when executed.


.. index:: protocol

Protocol
========

We have already seen part of the protocol implemented. In this section we will
describe each of the requests the client can send to the server.


Ping
----

When the client sends 4 bytes with the word ``ping`` to the server, the server
replies back with the word ``pong`` (another 4 bytes).

This request is for testing purposes only, but should be useful if you are
starting to implement a client from zero.


Reset
-----

When the client sends 5 bytes with the word ``reset`` the server will reset the
simulation, which means that any information related to the last or current
simulation will be deleted.

This request is useful to be executed always when starting the client, to make
sure the server starts with a client state too.

The server always replies back with an ``ok``.

Here is a simple ``reset`` example implemented in Python, which is almost the
same as with the ``ping`` request:

.. code:: python

   import zmq


   ctx = zmq.Context()
   req = ctx.socket(zmq.REQ)
   req.connect('tcp://127.0.0.1:6574')

   req.send(b'reset')

   reply = req.recv()
   print(reply)


Reading walls
-------------

The client can read walls at the current position. In order to do so, it must
send the current position to the server::

   <W><x-position><y-position><orientation>

The request is formed with 4 bytes:

#. ``W``: is the W byte character, idicating a request to read walls at the
   current position.
#. ``x-position``: is a byte number indicating the x-position of the mouse.
#. ``y-position``: is a byte number indicating the y-position of the mouse.
#. ``orientation``: a byte character, indicating the mouse orientation (``N``
   for North, ``E`` for East, ``S`` for South and ``W`` for West). Indicates
   where the mouse is heading to.

Positions are defined considering:

- Starting cell (x=0, y=0) is at the South-West.
- When going from West to East, the x-position increments.
- When going from South to North, the y-position increments.

The server replies with 3 bytes indicating the walls around the mouse.

#. First byte (boolean byte) indicates whether there is a wall to the left.
#. Second byte (boolean byte) indicates whether there is a wall to the front.
#. Third byte (boolean byte) indicates whether there is a wall to the right.

Here is an example in Python to read walls just after exiting the starting
cell, when we are at (x=0, y=1) position and heading north:

.. code:: python

   import struct
   import zmq


   ctx = zmq.Context()
   req = ctx.socket(zmq.REQ)
   req.connect('tcp://127.0.0.1:6574')

   req.send(b'W' + struct.pack('2B', 0, 1) + b'N')

   left, front, right = struct.unpack('3B', req.recv())
   print(left, front, right)


Sending exploration state
-------------------------

This is probably the most important and complex request. It basically sends
the current state of the client including the mouse current position, the
discovered walls so far and all the weights assigned to each cell in the maze.

The request looks like this:

#. ``S``: is the S byte character, idicating we are sharing the state.
#. ``x-position``: is a byte number indicating the x-position of the mouse.
#. ``y-position``: is a byte number indicating the y-position of the mouse.
#. ``orientation``: a byte character, indicating the mouse orientation (``N``
   for North, ``E`` for East, ``S`` for South and ``W`` for West). Indicates
   where the mouse is heading to.
#. ``C``: a byte character indicating how the cell numbers matrix is being
   transmitted. ``C`` means C-style. If that does not work well for you, try
   ``F``, for Fortran-style.
#. ``numbers``: a byte array of 256 bytes. Each byte represents a number.
#. ``C``: a byte character indicating how the walls matrix is being
   transmitted. ``C`` means C-style. If that does not work well for you, try
   ``F``, for Fortran-style.
#. ``walls``: a byte array of 256 bytes. Each byte represents a number.

Walls are defined with a bitmask:

- 2\ :sup:`0`: less significant bit. Set it to 1 to mark the cell as visited.
- 2\ :sup:`1`: Set it to 1 to specify East wall is present.
- 2\ :sup:`2`: Set it to 1 to specify South wall is present.
- 2\ :sup:`3`: Set it to 1 to specify West wall is present.
- 2\ :sup:`4`: Set it to 1 to specify North wall is present.

.. note:: The simulation server will store every state received until a reset
   occurs. This allows you to execute the full simulation as fast as possible
   and then navigate through the state history using the graphical interface.

Here is an example in Python to send a state with fake walls and cell numbers.
We set the same wall and an increasing number for all cells:

.. code:: python

   import struct
   import zmq


   ctx = zmq.Context()
   req = ctx.socket(zmq.REQ)
   req.connect('tcp://127.0.0.1:6574')

   req.send(b'reset')
   req.recv()

   numbers = list(range(256))
   walls = [2] * 256

   state = b'S' + struct.pack('2B', 0, 1) + b'N'
   state += b'C'
   state += struct.pack('256B', *numbers)
   state += b'C'
   state += struct.pack('256B', *walls)

   req.send(state)

   reply = req.recv()
   print(reply)

Now try and play a bit with that script:

- Change the mouse position and orientation.
- Change the walls sent.
- Change the numbers sent.
- Change ``C`` and ``F`` in the numbers sent to understand the differences.
- Remove the ``reset`` and see how the state history increases and how you can
  navigate through it.
