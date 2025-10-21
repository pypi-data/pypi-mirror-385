Introduction
============


.. image:: https://readthedocs.org/projects/adafruit-circuitpython-opt4048/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/opt4048/en/latest/
    :alt: Documentation Status


.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/adafruit/Adafruit_CircuitPython_OPT4048/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_OPT4048/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

CircuitPython driver library for the Adafruit OPT4048 breakout board, a high-speed, high-precision tristimulus XYZ color sensor.


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_
* `Register <https://github.com/adafruit/Adafruit_CircuitPython_Register>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

`Adafruit OPT4048 Tri-Stimulus XYZ Color and Lux Sensor <http://www.adafruit.com/products/6335>`_

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-opt4048/>`_.
To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-opt4048

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-opt4048

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install adafruit-circuitpython-opt4048

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install adafruit_opt4048

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

    import time
    from time import sleep

    import board

    from adafruit_opt4048 import OPT4048, ConversionTime, Mode, Range

    i2c = board.I2C()  # uses board.SCL and board.SDA
    # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
    sensor = OPT4048(i2c)

    sensor.range = Range.AUTO
    sensor.conversion_time = ConversionTime.TIME_100MS
    sensor.mode = Mode.CONTINUOUS
    while True:
        x, y, lux = sensor.cie
        print(f"CIE x:{x}, y:{y}, lux: {lux}", end=" ")
        print(f"K: {sensor.calculate_color_temperature(x,y)}")
        time.sleep(1)


Documentation
=============
API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/opt4048/en/latest/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_OPT4048/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
