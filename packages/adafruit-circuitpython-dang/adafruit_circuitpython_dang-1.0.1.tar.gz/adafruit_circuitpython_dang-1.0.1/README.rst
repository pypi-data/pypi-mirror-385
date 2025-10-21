Introduction
============


.. image:: https://readthedocs.org/projects/adafruit-circuitpython-dang/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/dang/en/latest/
    :alt: Documentation Status


.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/adafruit/Adafruit_CircuitPython_Dang/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_Dang/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

A subset of the curses framework. Used for making terminal based applications.


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.


Works with any displayio based display.

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-dang/>`_.
To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-dang

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-dang

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install adafruit-circuitpython-dang

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install adafruit_dang

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

    import time

    import supervisor
    import terminalio
    from displayio import Group, Palette, TileGrid
    from terminalio import Terminal

    import adafruit_dang as curses


    class Window:
        def __init__(self, n_rows, n_cols, row=0, col=0):
            self.n_rows = n_rows
            self.n_cols = n_cols
            self.row = row
            self.col = col

        @property
        def bottom(self):
            return self.row + self.n_rows - 1

        def up(self, cursor):  # pylint: disable=invalid-name
            if cursor.row == self.row - 1 and self.row > 0:
                self.row -= 1

        def down(self, buffer, cursor):
            if cursor.row == self.bottom + 1 and self.bottom < len(buffer) - 1:
                self.row += 1

        def horizontal_scroll(self, cursor, left_margin=5, right_margin=2):
            n_pages = cursor.col // (self.n_cols - right_margin)
            self.col = max(n_pages * self.n_cols - right_margin - left_margin, 0)

        def translate(self, cursor):
            return cursor.row - self.row, cursor.col - self.col


    def helloworld_main(stdscr, terminal_tilegrid):
        window = Window(terminal_tilegrid.height, terminal_tilegrid.width)
        stdscr.erase()
        img = [None] * window.n_rows

        user_input = ""
        user_entered_message = ""
        last_key_press = ""

        def setline(row, line):
            if img[row] == line:
                return
            img[row] = line
            line += " " * (window.n_cols - len(line) - 1)
            stdscr.addstr(row, 0, line)

        while True:
            header = "Hello World Adafruit Dang"
            margin = (window.n_cols - 1 - len(header)) // 2
            setline(1, f"{' ' * margin}{header}")

            key_press_message = f"Last key pressed: {last_key_press}"
            margin = (window.n_cols - 1 - len(key_press_message)) // 2
            setline(4, f"{' ' * margin}{key_press_message}")

            last_entered = f"Entered Message: {user_entered_message}"
            margin = (window.n_cols - 1 - len(last_entered)) // 2
            setline(6, f"{' ' * margin}{last_entered}")

            user_input_row = window.n_rows - 2
            if user_input:
                setline(user_input_row, user_input)
            else:
                setline(user_input_row, " " * (window.n_cols - 1))

            status_message_row = terminal_tilegrid.height - 1
            status_message = f" Adafruit Dang | Demo | Fruit Jam | {int(time.monotonic())}"
            status_message += " " * (window.n_cols - len(status_message) - 1)
            line = f"{status_message}"
            setline(status_message_row, line)

            k = stdscr.getkey()
            if k is not None:
                if len(k) == 1 and " " <= k <= "~":
                    user_input += k
                    last_key_press = k
                elif k == "\n":
                    user_entered_message = user_input
                    user_input = ""
                elif k in {"KEY_BACKSPACE", "\x7f", "\x08"}:
                    user_input = user_input[:-1]


    def run_helloworld_main(terminal, terminal_tilegrid):
        return curses.custom_terminal_wrapper(terminal, helloworld_main, terminal_tilegrid)


    main_group = Group()
    display = supervisor.runtime.display
    font = terminalio.FONT
    char_size = font.get_bounding_box()
    print(f"char_size: {char_size}")
    screen_size = (display.width // char_size[0], display.height // char_size[1])

    terminal_palette = Palette(2)
    terminal_palette[0] = 0x000000
    terminal_palette[1] = 0xFFFFFF

    terminal_area = TileGrid(
        bitmap=font.bitmap,
        width=screen_size[0],
        height=screen_size[1],
        tile_width=char_size[0],
        tile_height=char_size[1],
        pixel_shader=terminal_palette,
    )

    main_group.append(terminal_area)
    terminal = Terminal(terminal_area, font)

    display.root_group = main_group

    run_helloworld_main(terminal, terminal_area)


Documentation
=============
API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/dang/en/latest/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_Dang/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
