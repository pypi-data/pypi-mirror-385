SPanish INquisition (spin)
==========================

A web-based tool for showing information obtained from things on a rack
(i.e. usually devices connected to control boxes).

Requirements
------------

Spin requires the `aiohttp` and `mlzlog` Python packages.  For accessing Tango
and PILS devices, `pytango` and `zapf` are required, respectively.

Demo
----

There is a configuration for testing in the `demo` directory.  It connects to
all supported backends, exercises most features of the frontend and also
provides a custom plugin example.

Running `bin/spin` from a Git checkout will use that configuration instead of
looking in `/etc/spin` by default.

Documentation
-------------

Is available in `doc/`, build it using Sphinx.
