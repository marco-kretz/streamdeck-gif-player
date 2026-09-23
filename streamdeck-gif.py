#!/usr/bin/env python3
# Plays an image/GIF across all Stream Deck keys as one big display.
# usage: uv run --with streamdeck --with pillow streamdeck-gif.py file.gif [gap_px]
import itertools
import sys
import time

from PIL import Image, ImageOps, ImageSequence
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

# Virtual pixels hidden behind the bezel between keys, so lines stay straight across keys.
GAP = int(sys.argv[2]) if len(sys.argv) > 2 else 0

deck = DeviceManager().enumerate()[0]
deck.open()
deck.reset()
rows, cols = deck.key_layout()
kw, kh = deck.key_image_format()["size"]
W, H = cols * kw + (cols - 1) * GAP, rows * kh + (rows - 1) * GAP

frames = []
for f in ImageSequence.Iterator(Image.open(sys.argv[1])):
    img = ImageOps.fit(f.convert("RGB"), (W, H))
    keys = []
    for r in range(rows):
        for c in range(cols):
            x, y = c * (kw + GAP), r * (kh + GAP)
            keys.append(PILHelper.to_native_key_format(deck, img.crop((x, y, x + kw, y + kh))))
    frames.append((keys, f.info.get("duration", 100) / 1000))

try:
    for keys, dur in itertools.cycle(frames):
        start = time.monotonic()
        with deck:
            for k, data in enumerate(keys):
                deck.set_key_image(k, data)
        time.sleep(max(0, dur - (time.monotonic() - start)))
except KeyboardInterrupt:
    pass
finally:
    with deck:
        deck.reset()
        deck.close()
