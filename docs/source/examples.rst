********
Examples
********


Protocol tester in Python
=========================

The Micromouse Maze Simulator project includes an example to test the
communication protocol. Only the code required for the client requests is
implemented, with no actual mouse search logic.

The `standalone tester example can be found as a script in the project
<https://github.com/Bulebots/mmsim/blob/master/examples/client_tester.py>`_.


Python solvers
==============

The Micromouse Maze Simulator project includes a couple of solvers implemented
in Python.

It is recommended to understand them in order, according to their complexity:

#. `A left wall follower example`_, which is able to follow the left wall, but
   is insufficient to solve most competition mazes.
#. `A simple solver example`_, which by simply incrementing a counter for each
   cell it passes through by 1 is able to solve all mazes eventually.
#. `A flood fill solver example`_, which efficiently solves all mazes
   eventually.


A real micromouse solver in C
=============================

A real, complete micromouse client implemented in C can be found in the
`Bulebule micromouse project <https://github.com/Bulebots/bulebule/>`_. This
client executes the search algorithm that effectively runs in the Bulebule
micromouse robot, implementing only the required functions to communicate with
the Micromouse Maze Simulation server.

To try that client you need to first download the Bulebule repository::

   git clone https://github.com/Bulebots/bulebule.git

Then change to the ``scripts/`` directory and compile the client::

   cd bulebule/scripts/
   make

.. note:: You need to have ZMQ libraries installed in your system in order to
   compile the project.

Now simply run the client while the Micromouse Maze Simulator is running!


.. _A left wall follower example:
   https://github.com/Bulebots/mmsim/blob/master/examples/client_leftwall.py
.. _A simple solver example:
   https://github.com/Bulebots/mmsim/blob/master/examples/client_simple.py
.. _A flood fill solver example:
   https://github.com/Bulebots/mmsim/blob/master/examples/client_floodfill.py
