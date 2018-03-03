.. autov documentation master file, created by
   sphinx-quickstart on Fri Jan 27 18:20:52 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to autov's documentation!
=================================

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    decenter   
    polcal

Using Auto V
------------
To make use of autov we need a Windows system with CODE V installed on it.
Ideally this is a computer we administer, because we'll also need cygwin. My
personal setup when developing this was Windows 7 on a virtual machine (using
VirtualBox) running on a linux host. This setup allowed me to automate the CODE
V analysis to output to a shared directory so that data could then be quickly
analyzed using a sane development environment on linux.

Auto V Object
-------------

.. automodule:: autov.autov

.. autoclass:: AutoV
    :members:

.seq File Parsing
-----------------

.. automodule:: autov.parse_seq
    :members:
    :private-members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
