.. Reactions documentation master file, created by
   sphinx-quickstart on Thu Nov 14 14:03:45 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Reactions's documentation!
=====================================

This package is used to define nuclear reactions, which are data objects that
contain information about nuclear reactions, such as fission, (n,2n) and so
on.

This package provides several classes, each one meant for a different type of
use. 
Reactions are (a->b) transmutations between two specific isotopes.
ProtoReactions are reactions of a given type on a given parent isotope, such
as U235(n,f).

If you are looking at this package for anything except to import its classes
with information you can supply from elsewhere, then you are going beyond
what we expect this package to be used for.
We will still gladly help! Contact us by email if you need any assistance.

Installation
------------
Installation is currently available through pip, and we're working on a conda
version as we speak (proverbially).


.. toctree::
   :hidden:
   :maxdepth: 2

   reactions
   tests

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
