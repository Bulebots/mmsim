.. index:: usage


*****
Usage
*****


.. index:: requirements

Requirements
============

In order to use the Micromouse Maze Simulator you need:

- Python 3.5 (or higher).


.. index:: installation

Installation
============

Installation is very straight-forward using Python's ``pip``::

   pip3 install --user mmsim

This will install all the required dependencies and will provide you with the
``mmsim`` command.


.. index:: launching

Launching
=========

To run the simulator simply::

   mmsim

This will, the first time, download a set of mazes from `micromouseonline
<https://github.com/micromouseonline/mazefiles>`_.

If you have a local maze files collection in text format you may use that
instead::

   mmsim your/local/collection/path/
