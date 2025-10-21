# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 Thomas@chriesibaum.dev

"""
cb_key_stroke - The python loop key pressed interupt module

cb_key_stroke is a small module to quit/terminate a loop of a console app
by simply pressing a key. The beauty is that this module is running on Linux,
Öpfel-Rechnern as well Fenster operated computers.

Have fun while using the cb_key_stroke module!
Thomas
"""

import os
import sys


class CBKeyStrokeBase():
    """
    The KeyStrokeBase class which provides the core and common methods.
    """

    @classmethod
    def kbhit(cls):
        """
        Just do nothing. This method is overwritten when needed
        """
        return None

    @classmethod
    def getch(cls):
        """
        Just do nothing. This method is overwritten when needed
        """
        return None

    def check(self, keys=['\x1b', 'q']):   # pylint: disable=dangerous-default-value    W0102
        """
        Checks whether a button from the keys list has been pressed.

        Args:
            keys (list):    List of keys to check

        Return:
            Bool:       True if a key was pressed, False if not
        """
        if self.kbhit():
            c = self.getch()
            if c in keys:         # x1b is ESC
                return True

        return False


if 'linux' in sys.platform:

    if os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
        import select
        import tty
        import termios

        class CBKeyStroke(CBKeyStrokeBase):
            """
            linux KeyStroke implementation for foreground process'
            """

            def __init__(self):
                self.old_settings = termios.tcgetattr(sys.stdin)
                tty.setcbreak(sys.stdin.fileno())

            def __del__(self):
                termios.tcsetattr(
                    sys.stdin, termios.TCSADRAIN, self.old_settings)

            @classmethod
            def kbhit(cls):
                """
                check if a key was pressed and return it

                Return:
                    Bool:   True if a character was pressed, False if not
                """
                return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

            @classmethod
            def getch(cls):
                """
                Get the pressed character. Check first with kbHit if a key was
                pressed.

                Return:
                    char:   The pressed character
                """
                c = sys.stdin.read(1)
                return c
    else:
        class CBKeyStroke(CBKeyStrokeBase):
            """
            linux KeyStroke implementation for background process'
            """

            def __init__(self):
                pass


elif 'win' in sys.platform:
    import msvcrt   # pylint: disable=E0401

    class CBKeyStroke(CBKeyStrokeBase):
        """
        "Fensterli" Operating System KeyStroke implementation
        """

        def __init__(self):
            pass

        @classmethod
        def kbhit(cls):
            """
            check if a key was pressed and return it

            Return:
                Bool:   True if a character was pressed, False if not
            """
            return msvcrt.kbhit()

        @classmethod
        def getch(cls):
            """
            Get the pressed character. Check first with kbHit if a key was
            pressed.

            Return:
                char:   The pressed character
            """
            c = msvcrt.getch()
            c = c.decode("utf-8")
            return c

else:
    class CBKeyStroke(CBKeyStrokeBase):
        """
        Os not detected - KeyStroke is not implemented
        """

        def __init__(self):
            raise Exception(  # pylint: disable=broad-exception-raised
                f"KeyStroke is not implemented for this OS: {sys.platform}")
