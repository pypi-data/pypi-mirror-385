========
rtcirqus
========

Introduction
------------

rtcirqus, real-time config IRQ udev service, is a Python script that sets the
real-time priority of IRQ threads of onboard and USB audio interfaces
automatically using udev. It is heavily inspired by Joakim Hernberg's
`udev-rtirq <https://github.com/jhernberg/udev-rtirq/>`_ project. It is
especially useful when using ALSA directly or when using JACK. It can also be
used with PipeWire but currently this hasn't been tested extensively.

Features
--------
- Automatic real-time prioritisation of onboard audio devices.
- Automatic real-time prioritisation of USB audio and MIDI devices upon 
  connection and disconnection.
- Custom real-time prioritisation of audio devices.

Installation
------------
rtcirqus needs at least Python 3.6 and the following Python modules:

- pyalsaaudio
- psutil
- pyudev

On a Debian 12 system these modules can be installed with the following 
command:

::

 sudo apt install python3-alsaaudio python3-psutil python3-pyudev

Clone this repository:

::

  git clone https://codeberg.org/autostatic/rtcirqus.git

Copy ``src/rtcirqus/rtcirqus.py`` to ``/usr/local/bin/rtcirqus``:

::

  sudo cp src/rtcirqus/rtcirqus.py /usr/local/bin/rtcirqus
  sudo chmod 755 /usr/local/bin/rtcirqus

Copy ``resources/99-rtcirqus.rules`` to ``/etc/udev/rules.d/``:

::

  sudo cp resources/99-rtcirqus.rules /etc/udev/rules.d/

And reload the udev rules:

::

  sudo udevadm control --reload-rules

Optionally you could copy ``rtcirqus.conf`` to ``/etc/rtcirqus.d/rtcirqus.conf``:

::

  sudo mkdir /etc/rtcirqus.d/
  sudo cp resources/rtcirqus.conf /etc/rtcirqus.d/rtcirqus.conf

And modify it to your needs. So far the ``deny_list``, ``prio_list``, 
``prio_max`` and ``prio_step`` options are available. The ``deny_list`` and 
``prio_list`` options take a comma separated list of device names as produced
by ``rtcirqus`` itself or by ``aplay -l``. In the case of ``aplay -l`` the
device names are the names between the brackets. For more information on the
rtcirqus configuration file see `The configuration file`_.


Installation in a Virtual Environment
-------------------------------------

To install the ``rtcirqus`` project in a Python virtual environment for development:

::

  cd /path/to/clone/of/rtcirqus
  python3.9 -m venv /path/to/venv  # Python >= 3.9
  /path/to/venv/bin/pip install -e .

``pip`` will install the dependencies, and create a script, ``rtcirqus`` in its
``bin/`` directory, which you can run directly:

::

  /path/to/venv/bin/rtcirqus --help


You can then copy that script to ``/usr/local/bin/rtcirqus``:

::

  sudo cp /path/to/venv/bin/rtcirqus /usr/local/bin/

and proceed as above, adding ``udev`` rules and copying / updating configuration.


Overview
--------
You can now check if rtcirqus works properly by running it as a normal user. It
will produce output similar to the following:

::

  $ rtcirqus 
  WARNING: No configuration file found, continuing with defaults
  INFO: Loaded kernel is using threaded IRQS and threaded IRQ processes detected
  INFO: Onboard cards found: HD-Audio Generic, HD-Audio Generic, acp63
  INFO: USB cards found: Babyface (23596862)
  ERROR: Not running as root, rtcirqus needs to be run as root in order to set IRQ priorities

You can check if rtcirqus gets triggered by udev by plugging in a USB device
while running ``sudo journalctl -f | grep -E "kernel|rtcirqus"``. You should see something in the lines of:

::

 Sep 22 20:56:08 lenovo kernel: usb 7-1: new high-speed USB device number 8 using xhci_hcd
 Sep 22 20:56:08 lenovo kernel: usb 7-1: New USB device found, idVendor=0424, idProduct=3fb7, bcdDevice= 0.01
 Sep 22 20:56:08 lenovo kernel: usb 7-1: New USB device strings: Mfr=1, Product=2, SerialNumber=3
 Sep 22 20:56:08 lenovo kernel: usb 7-1: Product: Babyface (23596862)
 Sep 22 20:56:08 lenovo kernel: usb 7-1: Manufacturer: RME
 Sep 22 20:56:08 lenovo kernel: usb 7-1: SerialNumber: 18C0A73560538C8
 Sep 22 20:56:08 lenovo kernel: usb 7-1: Quirk or no altset; falling back to MIDI 1.0
 Sep 22 20:56:08 lenovo systemd[1]: Started run-rbb0fc57dc9614ca88fe1df4fae086cde.service - /usr/local/bin/rtcirqus --action add --dev-path /devices/pci0000:00/0000:00:08.3/0000:66:00.4/usb7/7-1/7-1:1.0/sound/card0.
 Sep 22 20:56:08 lenovo rtcirqus[9531]: INFO: Loaded kernel is using threaded IRQs and threaded IRQ processes detected
 Sep 22 20:56:08 lenovo rtcirqus[9531]: INFO: Onboard cards found: HD-Audio Generic, HD-Audio Generic, acp63
 Sep 22 20:56:08 lenovo rtcirqus[9531]: INFO: USB cards found: Babyface (23596862)
 Sep 22 20:56:08 lenovo rtcirqus[9531]: INFO: Setting RT priority 90 for USB card Babyface (23596862) with IRQ 49
 Sep 22 20:56:08 lenovo rtcirqus[9531]: INFO: Setting RT priority 85 for onboard card HD-Audio Generic with IRQ 91
 Sep 22 20:56:08 lenovo rtcirqus[9531]: INFO: Setting RT priority 80 for onboard card HD-Audio Generic with IRQ 92
 Sep 22 20:56:08 lenovo rtcirqus[9531]: INFO: Setting RT priority 75 for onboard card acp63 with IRQ 90

.. _The configuration file:

The configuration file
----------------------
rtcirqus accepts an INI-style configuration file of which the path can be 
passed to rtcirqus with the ``-c`` or ``--configuration`` option. By default 
rtcirqus looks for ``/etc/rtcirqus.d/rtcirqus.conf``.

The following parameters can be adjusted with the rtcirqus configuration file:

- **deny_list**: A comma separated list of audio or MIDI devices that will be
  excluded from getting a real-time priority. Example:
  
  ::
  
   deny_list = acp63, HD-Audio Generic
  
  The device names rtcirqus accepts can be found with `aplay -l`. The device
  names are the names between the brackets.
- **prio_list**: A comma separated list of audio or MIDI devices that will get
  a real-time priority corresponding to the order they are in. So the first
  device will get the highest real-time priority followed by any other device
  in this list. If there are more devices on the system then there are defined
  in this list then those will get the next available real-time priority. By
  default rtcirqus will assign real-time priorities according to the index ALSA
  assigns to the devices available on the system. So the device (or card within
  the ALSA context) with index 0 will get the highest priority.
- **prio_max**: The maximum real-time priority rtcirqus will set. The default
  is 90.
- **prio_step**: The size of the steps between the real-time priorities
  assigned by rtcirqus. The default is 5.


Future plans
------------
- Always give audio or MIDI device that gets plugged in the highest priority.
- Improve handling of USB devices connected to USB2 ports using the ehci_hcd kernel module
- Add an option to choose between static mode and dynamic mode:
  
  - Static mode: priorities of connected devices stay the same upon connection
    or disconnection of devices (the current default).
  - Dynamic mode: priorities of connected devices get reinitialised upon
    connection or disconnection of devices.
- Add possibility to prioritise USB or onboard devices separately.
- Think of a logo.

Contact
-------

To contact me send me a mail or if it's a technical issue or question, use 
the project's issue tracker at `codeberg.org
<https://codeberg.org/autostatic/rtcirqus/issues>`_.
