#!/usr/bin/env python3

# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 Thomas@chriesibaum.dev

"""
cb_key_stroke_basic_usage.py - Example file for using the cb_key_stroke module
"""

import time
from cb_key_stroke import CBKeyStroke

k = CBKeyStroke()
print('Press ESC to terminate!')

while True:

    # do your stuff here, for this example we use a sleep and a print instead.
    time.sleep(0.5)
    print('.', end='', flush=True)

    # check whether a key from the list has been pressed
    if k.check(['\x1b', 'q', 'x']):
        break

print('\nfinito!')
