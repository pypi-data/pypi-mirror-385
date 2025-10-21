# pwconn -- manage Pipewire connections via TUI

`pwconn` serves the same basic function as `qpwgraph`: it allows
you to view, create, and remove connections between Pipewire
apps. It is a UI wrapper on the command-line utils `pw-cli`,
`pw-link`, and `aconnect`.

It is under development and not that pretty yet, but if you want
to play around with it most of the functionality is there.

<img width="1227" height="757" alt="pwconn-screenshot" src="https://github.com/user-attachments/assets/9b51e74b-c285-4504-a1fb-c2ef20df0310" />

Requirements:
* ['uv'](https://github.com/astral-sh/uv) for build/install (I
  wanted to give it a try, seems ok but jury is still out)
* `alsa-tools` from your Linux distribution, for the
  `aconnect` tool
* `pw-utils` from your Linux distribution, for the `pw-cli` and
  `pw-link` tools.


#### Build/install

The options are:

* Install latest release from PyPI: `pip install pwconn`
* Launch the project from the source tree with `uv run pwconn`
* Install from source locally
    * Build wheel with `uv build`
    * Optional: create and activate a virtualenv for the install
        * `python3 -m venv <destination>`
        * `. <destination>/bin/activate`
    * Install the wheel with `pip install dist/pwconn-0.1.0-py3-none-any.whl`
    * Launch as `pwconn`


#### Usage

* The main UI is a list of Pipewire devices of a single kind
(audio, JACK MIDI, ALSA MIDI, or video).

* Select a line in the list by up and down arrow keys or mouse click

* Keyboard commands are listed at the bottom of the screen

* The keys `[`, `]`, `{`, and `}` expand and collapse. Devices
expand to show ports, and ports expand to show connections

* The keys "a", "j", "m", and "v" switch which kind of device is
displayed

* When a port is selected, the space key will "mark" it.

* To make one or more connections, mark all of the connection
  endpoints and press "c". If there are multiple ins and outs
  selected it will make a reasonable choice of connections which
  is generally OK. If not, make the connections one at a time.

* To disconnect, select a link (from either "end") and type "d"

* If a "connect" or "disconnect" action does not appear to do anything,
  this is probably an error in the underlying operation that isn't reflected
  in the UI. In particular, ALSA MIDI connections may not be deleteable by
  a process that did not create them.
