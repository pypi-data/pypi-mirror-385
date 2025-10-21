# SPDX-FileCopyrightText: 2025 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""Simple test script for 3.7" 240x416 tricolor display (ThinkInk_370_Tricolor_BABMFGNR)."""

import time

import board
import busio
import displayio
from fourwire import FourWire

import adafruit_uc8253

displayio.release_displays()

# This pinout works on a MagTag with the newer screen and may need to be altered for other boards.
spi = busio.SPI(board.EPD_SCK, board.EPD_MOSI)  # Uses SCK and MOSI
epd_cs = board.EPD_CS
epd_dc = board.EPD_DC
epd_reset = board.EPD_RESET
epd_busy = board.EPD_BUSY

display_bus = FourWire(spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000)
time.sleep(1)

display = adafruit_uc8253.UC8253(
    display_bus, width=240, height=416, busy_pin=epd_busy, rotation=0, highlight_color=0xFF0000
)

g = displayio.Group()

pic = displayio.OnDiskBitmap("/display-ruler-1280x720.bmp")
t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
g.append(t)

display.root_group = g

display.refresh()

print("refreshed")

time.sleep(display.time_to_refresh + 5)
# Always refresh a little longer. It's not a problem to refresh
# a few seconds more, but it's terrible to refresh too early
# (the display will throw an exception when if the refresh
# is too soon)
print("waited correct time")


# Keep the display the same
while True:
    time.sleep(10)
