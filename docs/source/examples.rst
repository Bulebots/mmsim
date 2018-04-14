.. index:: examples


********
Examples
********


.. index:: client, tester, python

Protocol tester in Python
=========================

The Micromouse Maze Simulator project includes an example to test the
communication protocol. Only the code required for the client requests is
implemented, with no actual mouse search logic.

The `standalone tester example can be found as a script in the project
<https://github.com/Theseus/mmsim/blob/master/examples/client_tester.py>`_.


.. index:: client, simple, solver, python

Simple solver in Python
=======================

The Micromouse Maze Simulator project includes a fully working solver example
implemented in Python. This client implements a robot that is able to explore
the maze (i.e.: read and update walls, move...) while making decisions on
which move to make on each step.

The decision making is very simple:

- Each time the robot passes through a cell, it increments its associated
  weight by 1.
- It then looks around to see the possible moves it can make (i.e.: having a
  wall will prevent a movement in that direction).
- Among the possible moves, it will look at the weights of the next possible
  cells and select the lowest weight.
- It will move to the cell that has the lowest weight.

The `standalone simple solver example can be found as a script in the project
<https://github.com/Theseus/mmsim/blob/master/examples/client_simple.py>`_.

.. note:: There is a lot of code just to implement maze storage, adding walls,
   client-server communication... The decision making and the actual search
   algorithm is implemented in the last functions. In particular, the
   ``run_search()``, ``best_step()`` and ``recalculate_weights()`` functions.


.. index:: real, client, C, Bulebule

A real micromouse client in C
=============================

A real, complete micromouse client implemented in C can be found in the
`Bulebule micromouse project <https://github.com/Theseus/bulebule/>`_. This
client executes the search algorithm that effectively runs in the Bulebule
micromouse robot, implementing only the required functions to communicate with
the Micromouse Maze Simulation server.

To try that client you need to first download the Bulebule repository::

   git clone https://github.com/Theseus/bulebule.git

Then change to the ``scripts/`` directory and compile the client::

   cd bulebule/scripts/
   make

.. note:: You need to have ZMQ libraries installed in your system in order to
   compile the project.

Now simply run the client while the Micromouse Maze Simulator is running!
