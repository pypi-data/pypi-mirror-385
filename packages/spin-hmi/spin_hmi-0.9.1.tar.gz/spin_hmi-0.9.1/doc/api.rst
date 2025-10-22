.. _api:

Backend/Frontend API
====================

The communication between backend and frontend is done over a websocket. Right
now, the route for this is hardcoded in the frontend as `/ws` on the same host
that served the frontend page.

Messages
--------

All messages are sent as JSON.
There are currently three kinds of messages, :ref:`Updates <api_update>`,
:ref:`Requests <api_request>` and :ref:`Replies <api_reply>`.

.. _api_update:

Update
""""""

The basic message is the Update, which represents a status and value for one
device from the backend.  It is sent from the backend to all connected
frontends.  For readonly usage, this message is the only one that's needed.  The
following keys are included:

`key`
    An identifier.  Usually the device name or a special value for a common
    update.  Used by the frontend to identify the element to act upon.

`unit`
    String representing the physical unit of the `value`.

`state`
    Standardized string value representing the new state of the device. Has to
    be one of `ok`, `warn`, `busy`, `disabled`, `error` or `unknown`.

`state_str`
    A string with more information about the device's state.

`value`
    The value of the device. Can be an arbitrary JSON object.

All fields should be sent in each message.

As an example:

.. code:: json

    {
        "key": "cryo",
        "unit": "K",
        "state": "busy",
        "state_str": "cooling down",
        "value": 15.0
    }

The Common Update
"""""""""""""""""

As alluded to in the description of `key`, there is a special kind of update
identified by the key `__common__`.  It is therefore not associated with a
specific device but used for sending information about spin itself, currently
its hostname and the spin version.  The state is also used to display a warning
if the hostname is currently "localhost" (which indicates a network connectivity
problem).

.. code:: json

    {
        "key": "__common__",
        "unit": "",
        "state": "ok",
        "state_str": "",
        "value": {
            "hostinfo": "controlbox.local",
            "version": "Connected to Spin 3.14"
        }
    }

.. _api_request:

Request
"""""""

A message sent by the frontend to trigger an action in the backend.

`key`
    Identifies the device that should be acted upon.

`action`
    The action that triggered the request. Right now, there are `click` (mouse
    click),`confirm` ("yes" in a confirmation dialog) and `input` (numeric or
    string input).

`intent`
    The intended action the frontend wants to perform with the request. Can be
    `stop`, `reset`, `input`, `toggle`, `set` or `run`. For more info, see the
    section about :ref:`interactivity <api_interactive>`.

`data`
    The data sent with the request. Usually the new value to set on the device,
    or a null value if the intent doesn't require extra data.

`transform`
    If not null, manipulate the given value before using the result in the
    further interaction with the device. For example, if an element in spin
    should only act upon a subset of bits of a bitfield represented by a device,
    the `bits` transform makes the neccesary conversions in the backend so that
    only the specified bits are changed. Right now, the only available transform
    is `bits` (The frontend converts a configured `bit` transform into a
    one-width `bits`).

An example request will look like this:

.. code:: json

    {
        "key": "digital_output_device",
        "action": "input",
        "intent": "set",
        "data": "3",
        "transform": ["bits", 3, 5]
    }

.. _api_reply:

Reply
"""""

Sent from the backend to a specific frontend to trigger an action such as user
interaction.  This usually only happens in reaction to a request (usually to
request input or a confirmation).

The following keys are part of the message:

`key`
    Identifies the device where the interaction is needed.

`transform`
    Same as `transform` in :ref:`Request <api_request>`, should be sent back
    again in the re-request.

`action`
    String specifying the kind of action. Currently, there are three kinds of
    actions: `confirm` to prompt a confirmation by the user, `input` to show
    the user an input field appropriate to the device and `error` which
    requests the frontend to show an error message.

`data`
    JSON object with data appropriate for the type specified in `action`.

An example Reply asking for confirmation looks like this (for more info on the
contents of `data`, see :ref:`api_interactive`):

.. code:: json

    {
        "key": "cryo",
        "transform": null,
        "action": "confirm",
        "data": {
            "intent": "set",
            "data": 15.0,
            "what": "set on cryo",
            "prompt": "Are you sure?"
        }
    }

.. _api_interactive:

Interactivity
-------------

TODO: Describe available actions, intents and transforms.
Describe extensibility with new actions.
