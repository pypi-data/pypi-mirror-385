|pip| |pypi| |license|

SPanish INquisition (spin)
==========================

.. image:: resources/logo.svg
    :width: 100px
    :class: float-right

A web-based tool for showing information obtained from things on a rack
(i.e. usually devices connected to control boxes).

Requirements
------------

Spin requires the ``aiohttp`` and ``mlzlog`` Python packages.  For accessing
Tango and PILS devices, ``pytango`` and ``zapf`` are required, respectively.

Demo
----

There is a configuration for testing in the ``demo`` directory.  It connects to
all supported backends, exercises most features of the frontend and also
provides a custom plugin example.

Running ``bin/spin`` from a Git checkout will use that configuration instead of
looking in ``/etc/spin`` by default.

Documentation
-------------

The built version of the documentatin in ``doc`` `can be found here
<https://forge.frm2.tum.de/public/doc/spin/master/>`_.

.. |pip| image:: resources/badge-pip.svg
.. |pypi| image:: https://img.shields.io/pypi/v/pybadges.svg
.. |license| image:: resources/badge-license.svg
