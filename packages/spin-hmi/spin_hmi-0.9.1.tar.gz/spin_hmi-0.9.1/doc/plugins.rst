.. _plugins:

Plugins
=======

For information how to configure the plugins to be used by the server, see
:ref:`config`.

Builtin Plugins
---------------

Currently, there is only one built-in plugin.

Lakeshore Curve Handling
~~~~~~~~~~~~~~~~~~~~~~~~

A plugin to down- and upload Lakeshore calibration files in .340 format.

It can be included on a page by including an element with the following
`data-spin` attribute::

    <div data-spin="@devname custom=lakeshore"></div>

(where `devname` is the name of the backend device from the Spin config).

Will create a button to scan the curves from the lakeshore. The curves are
displayed as a table with the standard header informations, and buttons for up-
and download. Without an element with the appropriate id, the plugin does
nothing.

Currently, there is only one protocol available, which is `lsfile+tango://`. It
connects to the lakeshore through a tango-device with a `MultiCommunicate`
command (must follow the MLZ `StringIO
<https://forge.frm2.tum.de/entangle/defs/entangle-master/stringio/#StringIO.MultiCommunicate>`_
specification).

Custom Plugins
--------------

For loading the plugin, the function `init_plugin` has to exist and return a
dictionary with the following keys:

`protos`
    A dictionary where the keys are the protocols the Plugin wants to use and
    each value is the device class to be used for that protocol.

`assets`
    A list of strings, where each string will be interpreted as a filename
    relative to the plugin's directory. These files will be served with all
    pages.
