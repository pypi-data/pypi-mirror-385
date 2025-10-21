#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 Thomas@chriesibaum.com

import sys
import os
import time

from key_stroke import KeyStroke
from cb_logging import CBLogger
log = CBLogger(log_to_file=False)

# Try to import from parent directory first (for development),
# then use installed package
try:
    # Add the parent directory (project root) to Python path for development/testing
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # Try importing from local development version
    from cb_gwi_gpp import CBGwiGpp
    log.warning("Using local development version of cb_gwi_gpp")
except ImportError:
    try:
        from cb_gwi_gpp import CBGwiGpp
        log.info("Using installed version of cb_gwi_gpp")
    except ImportError as e:
        log.error(f"Could not import cb_gwi_gpp: {e}")
        sys.exit(1)


def main():
    log.info("Starting example0.py")


    s = CBGwiGpp(verbose=True)
    s.get_instrument_list()

    # try to find the GWI GPP instrument
    resource = s.get_gwi_gpp_resource('GPP-4323')

    if resource is None:
        log.error("GWI GPP instrument not found. Exiting.")
        sys.exit(1)
    else:
        resource = 'ASRL/dev/ttyUSB0::INSTR'  # e.g. for linux
    #    resource = 'ASRL4::INSTR'  # e.g. for the fensterli OS

    s.open(resource)

    s.set_channel(1, voltage=3.3, current=3)
    s.set_channel(2, voltage=12.0, current=0.2)

    s.output_on()

    k = KeyStroke()
    print('Press ESC to terminate!')
    while True:
        s.print_measurements()

        # check whether a key from the list has been pressed
        if k.check(['\x1b', 'q', 'x']):
            break
        time.sleep(1)

    s.output_off()

    s.close()

if __name__ == "__main__":
    main()
