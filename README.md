# streamdeck-gif-player

Plays an image or animated GIF across all keys of an Elgato Stream Deck, so the keys together form one large display.

Tested with the Stream Deck MK.2 (15 keys, 5×3). Other models supported by [python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck) should work too, since the key layout and image format are read from the device.

> **Linux only for now.** The setup below (udev rule, hidapi) is Linux-specific. Other platforms are untested.

## Requirements

- [uv](https://docs.astral.sh/uv/) (installs the Python dependencies `streamdeck` and `pillow` on the fly)
- `hidapi` system library, e.g. `sudo pacman -S hidapi` (Arch) or `sudo apt install libhidapi-libusb0` (Debian/Ubuntu)
- The official Stream Deck software, or tools like `streamdeck-ui`, must not be using the device at the same time

## Setup: udev rule

By default, only root can access the Stream Deck's HID device. This rule grants access to the logged-in user:

```sh
echo 'SUBSYSTEM=="hidraw", ATTRS{idVendor}=="0fd9", TAG+="uaccess"' | sudo tee /etc/udev/rules.d/70-streamdeck.rules
sudo udevadm control --reload
sudo udevadm trigger
```

Then unplug and replug the Stream Deck. `0fd9` is Elgato's USB vendor ID, so the rule covers all Stream Deck models.

## Usage

```sh
uv run --with streamdeck --with pillow streamdeck-gif.py fox-walk.gif
```

The animation loops until you stop it with `Ctrl+C`; the keys are cleared on exit.

Run it in the background:

```sh
nohup uv run --with streamdeck --with pillow streamdeck-gif.py fox-walk.gif >/dev/null 2>&1 &
pkill -INT -f streamdeck-gif.py   # stop and clear the keys
```

### Bezel gap

An optional second argument sets how many virtual pixels are hidden behind the bezel between keys (default `0`):

```sh
uv run --with streamdeck --with pillow streamdeck-gif.py some.gif 20
```

- `0`: every pixel of the image is shown; lines across keys appear slightly offset. Best for small or detailed content.
- `> 0`: lines stay straight across keys, but content under the bezels is lost.

For the sharpest result with `0`, use an image of `5×72 × 3×72` = **360×216 px** (for the MK.2). Other sizes are scaled and cropped to fit.

## Notes

- Each frame requires one USB transfer per key, so expect roughly 10–20 fps. Faster GIFs play slower than intended.
- `fox-walk.gif` is an original sample animation made for a 360×216 canvas with a gap of `0`.
