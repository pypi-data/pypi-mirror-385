Introduction
============


.. image:: https://readthedocs.org/projects/adafruit-circuitpython-mlx90632/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/mlx90632/en/latest/
    :alt: Documentation Status


.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/adafruit/Adafruit_CircuitPython_MLX90632/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_MLX90632/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

CircuitPython driver for the Adafruit MLX90632 FIR Remote Thermal Temperature Sensor - Medical Grade STEMMA QT / Qwiic


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

`Purchase one from the Adafruit shop <http://www.adafruit.com/products/6403>`_

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-mlx90632/>`_.
To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-mlx90632

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-mlx90632

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install adafruit-circuitpython-mlx90632

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install adafruit_mlx90632

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

	import time
	import board
	import adafruit_mlx90632

	i2c = board.I2C()
	mlx = adafruit_mlx90632.MLX90632(i2c)

	while True:
	    # Check if new data is available
	    if mlx.data_ready:
	        # Read temperatures
	        ambient_temp = mlx.ambient_temperature
	        object_temp = mlx.object_temperature
	        print(f"Ambient: {ambient_temp:.2f}°C, Object: {object_temp:.2f}°C")
	        # Reset new data flag
	        mlx.reset_data_ready()
	    time.sleep(0.1)

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/mlx90632/en/latest/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_MLX90632/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
