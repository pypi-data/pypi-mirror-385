Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-il0398/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/il0398/en/latest/
    :alt: Documentation Status

.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_IL0398/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_IL0398/actions
    :alt: Build Status

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

CircuitPython displayio drivers for IL0398 driven e-paper displays


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-il0398/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-il0398

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-il0398

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install adafruit-circuitpython-il0398

Usage Example
=============

.. code-block:: python

    """Simple test script for 4.2" 400x300 black and white displays.

    Supported products:
      * WaveShare 4.2" Black and White
        * https://www.waveshare.com/product/modules/oleds-lcds/e-paper/4.2inch-e-paper.htm
        * https://www.waveshare.com/product/modules/oleds-lcds/e-paper/4.2inch-e-paper-module.htm
      """

    import time
    import board
    import displayio
    import fourwire
    import adafruit_il0398

    displayio.release_displays()

    # This pinout works on a Feather M4 and may need to be altered for other boards.
    spi = board.SPI() # Uses SCK and MOSI
    epd_cs = board.D9
    epd_dc = board.D10
    epd_reset = board.D5
    epd_busy = board.D6

    display_bus = fourwire.FourWire(spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset,
                                     baudrate=1000000)
    time.sleep(1)

    display = adafruit_il0398.IL0398(display_bus, width=400, height=300, seconds_per_frame=20,
                                     busy_pin=epd_busy)

    g = displayio.Group()

    pic = displayio.OnDiskBitmap("/display-ruler.bmp")
    t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
    g.append(t)

    display.root_group = g

    display.refresh()

    time.sleep(120)


Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/il0398/en/latest/>`_.

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_IL0398/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
