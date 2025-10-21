Creating a display
==================

Display pages
-------------

Each page you :ref:`configure <config-pages>` consists of a
:file:`{pagename}.html` file, containing arbitrary HTML.  It should only contain
the content of the `<body>`; Spin will add the rest of the document structure
with the necessary references.

The generated HTML will automatically include a reference to
:file:`{pagename}.js` and :file:`{pagename}.css`, if they exist.  This is a good
place to put custom code and style definitions.

Additional data files can be referenced with the URL :file:`c/{filename}`.
I.e., SVG files can be included with ``<object data="c/example.svg"></object>``.

HTML display elements
---------------------

Elements that should display data, and/or interact with the user, must be
`<div>` or `<span>` tags and should be annotated with a `data-spin` attribute,
whose content has the following syntax::

    @name[.param] ["format"] [key[=value]] [key[=value]] ...

- The `name` needs to correspond to the name of one of the :ref:`configured
  devices <config-devices>`.  Parameters (which must also be specified in the
  configuration) of the devices are selected by the addition of `.param`.

  The special name `hostinfo` is always defined and shows the FQDN of the
  backend's machine, or "(disconnected)".

- If a format string is given enclosed in quotes, the element's text content
  will be replaced by the value of the device.  The format string is
  printf-style, and will be formatted with a single argument.  `{unit}` will be
  replaced by the device's (or parameter's) unit, if available.

  If no format string is given, only the device status is used to change the
  background of the element.

Further modifiers are given in `key` or `key=value` format. They are:

**Display modifiers**

``status``
    Instead of the value of a device, shows the status.  Automatically sets the
    format string to `"%s"`.

:file:`hl={cond}{val}`
:file:`hl={cond1}{val1},{cond2}{val2},...`
    Uses a special status highlight color if the status is OK and the current
    value of the device matches the condition for the value.  `cond` can be
    `=`, `<`, `<=`, `>`, `>=`.  `=` can be omitted.  Examples: `hl=5`,
    `hl=>100`, `hl=<=17`, `hl=open` (string values only work with `=`).

    You can give multiple conditions (one of them needs to be true) separated
    by commas.

:file:`nohl={cond}{val}...`
    Uses a special status highlight color if the status is OK and the current
    value of the device does *not* match the condition(s).

:file:`show={cond}{val}`
:file:`show={cond1}{val1},{cond2}{val2},...`
    Makes the element visible only if the current value of the device matches
    the condition, see `hl`.

    You can give multiple conditions (one of them needs to be true) separated
    by commas.

:file:`hide={cond}{val}...`
    Like `show` but hides the element.

:file:`showstatus={states}`
    Makes the element visible only if the current status of the device matches
    one of the given comma-separated states.

    The possible values are ``ok``, ``warn``, ``busy``, ``disabled``, ``error``
    and ``unknown``.

:file:`hidestatus={states}`
    Like `showstatus` but hides the element.

**Value transformation**

:file:`bit={n}`
    For integral devices, makes the display and user input act on only the
    specified bit.  Bit numbering starts at 0 for the LSB.

:file:`bits={m}-{n}`
    Like `bit`, but acts on a bitfield from bit *m* to *n*.

:file:`scale={factor}`
    For floating devices, scales incoming values by multiplying with
    `factor`, and user input values by dividing by it.

**Interaction modifiers**

All of these modifiers make the element user-interactable.  Interaction intents
are communicated to the backend, which will determine how to react, usually
depending on the status of the device.

``input``
    A click tells the backend that the user wants to input a new value.
    Usually, a numeric input dialog box will be shown, and when the new value
    is accepted, the device should set/move to that value.

``toggle`` or :file:`toggle={a},{b}`
    A click tells the backend that the user wants to toggle the device between
    the given values, or if just ``toggle`` is given, between 0 and 1.  If the
    device has a value other than the two toggle values, the first one is set.

:file:`set={val}`
    A click tells the backend that the user wants to set/move to the given
    value.

``stop``
    A click tells the backend that the user wants to stop the device.

``reset``
    A click tells the backend that the user wants to reset the device.

:file:`run={command}`
    A click tells the backend that the user wants to execute the given
    command, which is backend-specific.

**Custom hook**

This modifier marks the element with custom behavior.  Usually this is for a
backend's special feature or behavior added by plugins.

:file:`custom={name}`
    Name of the custom context for this element.  The documentation of the
    respective backend/plugin will tell when to use this, with what value.


SVG display elements
--------------------

In inkscape, instead of using a `data-spin` attribute, you use the inkscape
label (the `inkscape:label` attribute, which is easily editable in the "Layers
and Objects" dialog), to configure the behaviour of elements.  The syntax stays
the same as above.

Supported elements are groups (`<g>`), paths (`<path>`), rectangles (`<rect>`),
ellipses (`<ellipse>`) and text (`<text>`).

Since text elements cannot have a background, you need to combine a
path/rectangle and text element in a group to show the value and status of a
device.

A group with the proper `inkscape:label` automatically propagates to its
children, with text elements showing the value and path/other shapes showing the
status via fill color.

Note that this goes only one layer deep, so you can "protect" an element from
getting its fill color changed by nesting it in another subgroup of the group.


Plots
-----

Plots of device values can be added in a similar way to simple fields.

In **HTML**, they must be a `<div>` element with a `data-spin-plot` attribute
following the syntax below.

In **SVG**, they must be a `<rect>` element with the `inkscape:label` set to
`!plot ` and then the content of the `data-spin-plot` attribute for HTML.

The attribute syntax is::

    ["title"] [key[=value]] @name[.param] ["label"] [key[=value]] ... @name[.param] ["label"] ...

In other words, similar to the syntax for simple fields, but with a title and
common modifiers followed by multiple groups with `@name`\s, with each creating
a single curve in the plot.  The `label` for each curve sets its legend text.

The available modifiers for the whole plot are:

:file:`interval={n}`
    Specifies the interval for plot data in minutes (default: 60).

:file:`fontsize={n}`
    Sets the basic font size for the plot (default: 14).

`legend=right` or `legend=bottom` or `legend=none`
    Sets the legend position or visibility (default: bottom).

`logscale`
    Specifies logarithmic Y scaling.

The available modifiers for individual curves are:

:file:`color={name}`
    Specifies the curve's color (default: automatic), with an HTML color name or
    `#rrggbb` hex number.

`y2`
    Specifies that the curve should use a secondary Y axis.
