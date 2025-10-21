Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-st7789/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/st7789/en/latest/
    :alt: Documentation Status

.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_ST7789/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_ST7789/actions/
    :alt: Build Status

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

displayio driver for ST7789 TFT-LCD displays.

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython 4.0.0-beta.0+ <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Usage Example
=============

.. code-block:: python

    import board
    import displayio
    # Starting in CircuitPython 9.x fourwire will be a seperate internal library
    # rather than a component of the displayio library
    try:
        from fourwire import FourWire
    except ImportError:
        from displayio import FourWire

    from adafruit_st7789 import ST7789

    displayio.release_displays()

    spi = board.SPI()
    while not spi.try_lock():
        pass
    spi.configure(baudrate=24000000) # Configure SPI for 24MHz
    spi.unlock()
    tft_cs = board.D5
    tft_dc = board.D6

    display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=board.D9)

    display = ST7789(display_bus, width=240, height=240, rowstart=80, bgr=True, invert=True)

    # Make the display context
    splash = displayio.Group()
    display.root_group = splash

    color_bitmap = displayio.Bitmap(240, 240, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = 0xFF0000

    bg_sprite = displayio.TileGrid(color_bitmap,
                                   pixel_shader=color_palette,
                                   x=0, y=0)
    splash.append(bg_sprite)

    while True:
        pass

Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/st7789/en/latest/>`_.

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_ST7789/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
