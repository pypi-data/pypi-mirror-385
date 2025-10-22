# roboflex.webcam_gst

Support for USB and built-in webcams using GStreamer. This module is a drop-in alternative to `roboflex_webcamuvc`, but it avoids the libuvc dependency and instead drives cameras through the GStreamer stack. The message schema and Python/C++ APIs are kept as close as possible to the original UVC implementation.

## System dependencies

GStreamer and its development headers are required at build time:

```bash
# Ubuntu / Debian
sudo apt install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev gstreamer1.0-plugins-good

# macOS (Homebrew)
brew install gstreamer gst-plugins-base gst-plugins-good
```

## Install

The project can be built like other roboflex modules:

```bash
pip install roboflex.webcam_gst
```

or from source with CMake.

## Python usage

```python
import roboflex.webcam_gst as rcw

print(rcw.get_device_list_string())

sensor = rcw.WebcamSensor(
    width=640,
    height=480,
    fps=30,
    device_index=-1,  # use default camera
    format="",  # empty string lets GStreamer pick
    emit_rgb=True,
)

sensor.start()
try:
    # consume messages...
    pass
finally:
    sensor.stop()
```

The emitted messages (`WebcamDataRGB` / `WebcamDataRaw`) match the original module so downstream nodes can continue to operate without changes.

## Device descriptors

`get_device_list()` returns `DeviceDescriptor` objects with the following fields:

- `display_name`: Human-readable label reported by GStreamer.
- `gst_factory_name`: The underlying factory name used by GStreamer.
- `device_class`: The class of device (e.g. `Video/Source`).
- `device_path`: OS-specific identifier when available.
- `caps_strings`: A list of capability structures advertised by the device.

## Notes

- RGB output is enabled by default. Set `emit_rgb=False` to receive raw frames; use the `format` parameter to request a specific pixel format string (e.g. `"NV12"` or `"YUY2"`), subject to what the device supports.
- The helper `WebcamRawToRGBConverter` currently expects RGB input; raise an exception otherwise. Most workflows should request RGB directly from the sensor.
- Because we rely on GStreamer, the available devices and pixel formats depend on the plugins installed on your system.
