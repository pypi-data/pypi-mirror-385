.. _config:

Configuring and running the server
==================================

Server command
--------------

.. parsed-literal::

    **spin** [-c *confdir*] [-v]

Runs the spin server daemon with the configuration directory given by `-c`, or
by default, `/etc/spin`.

Giving `-v` switches on debug logging.

A systemd unit file is provided in the source repository under `etc`.


Global configuration
--------------------

Spin is configured in a Python file called `conf.py`, to be placed in the
configuration directory.

Here is a simple example config file::

    from spin.config import Config, Device, Page, Param

    config = Config()
    config.server = '0.0.0.0:80'
    config.control_url = 'http://{host}:8080/'
    config.plugins = []
    config.pages = {
        'default': Page('default.html'),
    }
    config.devices = {
        'field':  Device('tango://localhost:10000/test/mag/field',
                         pollinterval=1.0,
                         params=[Param('ramp', 5.0)]),
        'sensor': Device('secop://localhost:10767/temp_sensor_1'),
    }

Basic config
~~~~~~~~~~~~

`Config.server`
    Local address to bind to.  Default is `0.0.0.0:8000`, which binds to all
    addresses on port 8000.  If you want to listen to the standard HTTP port 80,
    note that you need to have administrator privileges.

    Note that this is unencrypted HTTP, HTTPS is not supported so far.

`Config.control_url`
    If given, gives the URI of a page that will be shown as an iframe to the
    frontend user behind a "control" button.  It is intended to be a page where
    the user can, for example, start and stop services on the machine, e.g. with
    `Marche <https://marche.readthedocs.io/en/latest/>`_.  `{host}` is replaced
    by the machine's host.

    The default is `None`.

`Config.dark_theme`
    If `True` (default: `False`), the default theme for all pages will be set
    to dark. Keep in mind contrast and visibility when choosing this and prefer
    the light mode for displays in the sample environment racks. Currently, the
    interactive elements don't follow the theme correctly and SVGs and other
    assets will have to be made with the dark mode in mind. Intended mostly for
    read-only NICOS-Monitor-like setups in an office or hutch.

`Config.nav_bar`
    If `True` (default: `False`), Spin will insert a "navigation bar" at the top
    of the page content linking to each page using its title.

`Config.quick_icons`
    If `False` (default: `True`), Spin will not insert the "quick function
    icons" at the bottom of the page content with buttons to show errors,
    reload or navigate to the `control_url`.


Plugins
~~~~~~~

You can set `config.plugins` to a list of plugins that contain additional
backend device types and/or script and style assets for the frontend.

Plugins can either be specified via the path to a Python file (absolute or
relative to the configuration directory), or for built-in plugins, a module name
within `spin.plugins`.

For more information, see :ref:`plugins`.

.. _config-pages:

Pages
~~~~~

A Spin server can provide multiple pages to clients.  The `pages` dictionary
maps pagenames to `Page` entries.  Each page configured here is available on the
HTTP server as `/pagename`.

The `Page` constructor has the following fields:

`Page.file`
    The HTML file to serve content for this page, which must be present in the
    Spin configuration directory.

`Page.title`
    A string that will be used as the HTML title of the page, defaults to the
    pagename.

`Page.readonly`
    If `True`, the page will not accept user input, even if it is configured in
    the frontend data.  Defaults to `False`.

`Page.hidden`
    If `True`, the page will not be listed in automatically generated links when
    the `Config.nav_bar` value is true.  Defaults to `False`.

`Page.nav_bar`
    Overrides (with `True` or `False`) the global `Config.nav_bar` setting for
    this page.

`Page.quick_icons`
    Overrides (with `True` or `False`) the global `Config.quick_icons` setting
    for this page.

`Page.parent`
    This designates another page (given by pagename) as the logical "parent" of
    this page.  At the moment, this is only used for generating the navbar.
    `None` (the default) indicates a top-level page.

`Page.auth`
    A list of tuples of `(name, sha256_hash)` in order to make this page only
    accessible after authentication with one of the given user names and the
    respective password, which is given here in hexdigest form.  For example::

        hashed_pw = hashlib.sha256(b'sesame').hexdigest()
        config.pages = {
            'secret': Page('secret.html', auth=[('admin', hashed_pw)])
        }

    ``None`` or an empty list means no authentication is necessary.

.. _config-devices:

Devices
~~~~~~~

For each device that you want to show in the visualization, Spin needs an entry
in the `devices` dictionary.

The `Device` constructor has the following fields:

`Device.device`
    The URI for connecting to the device.  The URI syntax is described below for
    each supported backend.

`Device.pollinterval`
    For device backends that must poll actively, this specifies the poll
    interval in seconds, by default 1 second.

`Device.params`
    A list of parameters of the device that should be made available in addition
    to the device's main value.  The meaning of "parameter" is backend specific.

    Each entry can either be a parameter name or a `Param()` object in order to
    give a parameter-specific pollinterval: ``Param(name, pollinterval)``.  The
    custom pollinterval should be a multiple of the general device pollinterval
    and only has an effect for device backends that poll actively.

`Device.confirm`
    `None` (the default) or a string - in the latter case, the device backend
    will request a confirmation from clients for each interactive action
    attempted on the device, such as setting a value or toggling.  The given
    string will be shown to the user.

`Device.options`
    A dictionary of further backend specific options.


Tango devices
-------------

Represents a `Tango <https://tango-controls.org>`_ device.

URI syntax::

    tango://<database>:<port>/<domain>/<family>/<member>

Main device value is the Tango `value` attribute.  Parameters map to additional
parameters.

All devices and parameters are actively polled.

Additional options:

- `enum`: if True, and the device has a "mapping" property as defined `in
  the MLZ standard
  <https://forge.frm2.tum.de/entangle/defs/entangle-master/digitaloutput/#DigitalOutput.mapping>`_,
  the values are mapped to string on read, and mapped back to numeric values on
  write.


SECoP devices
-------------

Represents a specific module in a `SECoP <https://sampleenvironment.org/secop>`_
node.

URI syntax::

    secop://<host>:<port>/<module>

Main device value is the `value` parameter.

All values are provided by asynchronous updates, no polling is performed after
an initial activation request.

Additional options:

- `enum`: if True, and the device has an "enum" datainfo, the values are mapped
  to string on read, and mapped back to integers on write.


NICOS devices
-------------

Represents a `NICOS <https://nicos-controls.org>`_ device via connection to a
NICOS cache.

URI syntax::

    nicos://<cachehost>:<port>/<devkey>

Ususally, `devkey` is :file:`nicos/{devname}` with devname being the lowercased
NICOS device name.

Main device value is the `value` parameter.

All values are provided by asynchronous updates, no polling is performed after
an initial request.

The connection is read-only; interactive use is not possible.


PILS devices
------------

Represents a `PILS <https://forge.frm2.tum.de/public/doc/plc/master/html/>`_
device connected via the Zapf library.

Possible URI syntaxes:

``pils+ads://host[:port]/amsnetid:amsport#devname``
    Connection to a Beckhoff PLC using the ADS protocol.  The TCP port is 48898
    by default.  The AMS NetID and AMS port are specific to the PLC.  Note that
    an AMS router entry must be set on the PLC in order to connect.

    Example: ``pils+ads://192.168.201.2/5.18.77.4.1.1:851#motor``

``pils+modbus://host[:port]/slaveno#devname``
    Connection to a host that supports the Modbus/TCP protocol.  The TCP port is
    502 by default.

    Example: ``pils+modbus://192.168.201.2/0#motor``

``pils+tango://dbhost:dbport/tango/device/name#motor``
    Connection to a `Tango <https://tango-controls.org>`_ device which in turn
    connects to the PLC.

    The Tango device interface must conform to the `Profibus
    <https://forge.frm2.tum.de/entangle/defs/entangle-master/profibus/>`_
    Entangle interface specification.

    Example: ``tango://192.168.201.2:10000/box/plc/ads#motor``

``pils+sim:///filepath``
    "Connection" to a software-simulated PLC.  Zapf starts it in the same
    process when the address is requested.

Additional options:

- `enum`: if True, and the device has an "enum" type, the values are mapped
  to string on read, and mapped back to integers on write.


EPICS devices
-------------

Not yet implemented.
