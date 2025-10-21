Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-ssd1325/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/ssd1325/en/latest/
    :alt: Documentation Status

.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_SSD1325/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_SSD1325/actions
    :alt: Build Status

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

DisplayIO driver for grayscale OLEDs drive by SSD1325

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
PyPI <https://pypi.org/project/adafruit-circuitpython-ssd1325/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-ssd1325

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-ssd1325

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install adafruit-circuitpython-ssd1325

Usage Example
=============

.. code-block:: python

    import time
    import board
    import busio
    import displayio
    import fourwire
    import adafruit_ssd1325

    displayio.release_displays()

    # This pinout works on a Metro and may need to be altered for other boards.
    spi = busio.SPI(board.SCL, board.SDA)
    tft_cs = board.D9
    tft_dc = board.D8
    tft_reset = board.D7

    display_bus = fourwire.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset,
                                     baudrate=1000000)
    time.sleep(1)
    display = adafruit_ssd1325.SSD1325(display_bus, width=128, height=64)

Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/ssd1325/en/latest/>`_.

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_SSD1325/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
