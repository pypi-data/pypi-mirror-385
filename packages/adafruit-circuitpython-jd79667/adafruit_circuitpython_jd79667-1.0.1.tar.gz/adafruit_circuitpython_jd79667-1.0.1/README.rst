Introduction
============


.. image:: https://readthedocs.org/projects/adafruit-circuitpython-jd79667/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/jd79667/en/latest/
    :alt: Documentation Status


.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/adafruit/Adafruit_CircuitPython_JD79667/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_JD79667/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

CircuitPython library for the JD79667 e-paper driver IC


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

`Purchase one from the Adafruit shop <http://www.adafruit.com/products/6373>`_

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-jd79667/>`_.
To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-jd79667

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-jd79667

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install adafruit-circuitpython-jd79667

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install adafruit_jd79667

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

    import board
    import busio
    import displayio
    from fourwire import FourWire

    import adafruit_jd79667

    displayio.release_displays()

    spi = busio.SPI(board.EPD_SCK, board.EPD_MOSI)  # Uses SCK and MOSI
    epd_cs = board.EPD_CS
    epd_dc = board.EPD_DC
    epd_reset = board.EPD_RESET
    epd_busy = board.EPD_BUSY

    display_bus = FourWire(spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000)
    time.sleep(1)

    display = adafruit_jd79667.JD79667(
        display_bus,
        width=384,
        height=184,
        busy_pin=epd_busy,
        rotation=270,
        colstart=0,
        highlight_color=0xFFFF00,
        highlight_color2=0xFF0000,
    )

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/jd79667/en/latest/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_JD79667/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
