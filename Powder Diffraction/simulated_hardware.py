import threading

import numpy
from ophyd import Component, Device, Signal, DeviceStatus

from generate_data import make_random_peaks, generate_flat_field, generate_image


_shutter_state = {"state": "open"}


class Shutter(Signal):
    def put(self, value):
        _shutter_state["state"] = value
        super().put(value)


shutter = Shutter(name="shutter")
sample_selector = Signal(name="sample_selector", value=0)


# Map samples to patterns.
SHAPE = (512, 512)
patterns = {}
x = numpy.linspace(0, 30, num=3001)
intensities = {}
for i in range(5):
    intensity = make_random_peaks(x)
    image = generate_image(x, intensity, SHAPE)
    intensities[i] = intensity
    patterns[i] = image


class TimerStatus(DeviceStatus):
    """Simulate the time it takes for a detector to acquire an image."""

    def __init__(self, device, delay):
        super().__init__(device)
        self.delay = delay  # for introspection purposes
        threading.Timer(delay, self.set_finished).start()


class DiffractionDetector(Device):
    exposure_time = Component(Signal, value=1)
    image = Component(Signal, value=numpy.zeros(SHAPE))

    def trigger(self):
        t = self.exposure_time.get()
        # Start with a flat field.
        arr = generate_flat_field(SHAPE) * t
        if _shutter_state["state"] == "open":
            current_sample = sample_selector.get()
            pattern = patterns[current_sample]
            # Scale it by the exposure time.
            scaled_pattern = pattern * t
            arr += scaled_pattern
        self.image.set(arr)
        return TimerStatus(self, t)
    
    def collect_asset_docs(self):
        yield from []


detector = DiffractionDetector(name="detector")
