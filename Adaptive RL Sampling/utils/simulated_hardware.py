import threading

import numpy
import numpy as np
from ophyd import Component, Device, Signal, DeviceStatus
from bluesky.plan_stubs import mv

from .generate_data import generate_measured_image, SHAPE


sample_selector = Signal(value=0, name="sample_selector")


class TimerStatus(DeviceStatus):
    """Simulate the time it takes for a detector to acquire an image."""

    def __init__(self, device, delay):
        super().__init__(device)
        self.delay = delay  # for introspection purposes
        threading.Timer(delay, self.set_finished).start()


class DiffractionDetector(Device):
    # exposure_time = Component(Signal, value=1)
    image = Component(Signal, value=numpy.zeros(SHAPE))
    signal_to_noise = Component(Signal, value=0)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delay = 2  # simulated exposure time delay

    def trigger(self):
        "Generate a simulated reading with noise for the current sample."
        sample_number = sample_selector.get()
        arr, snr = generate_measured_image(sample_number)
        # Update the internal signal with a simulated image.
        self.image.set(arr)
        self.signal_to_noise.set(snr)
        # Simulate the exposure and readout time with a tunable "delay".
        return TimerStatus(self, self.delay)

    def collect_asset_docs(self):
        yield from []


detector = DiffractionDetector(name="detector")


def select_sample(sample_number):
    yield from mv(sample_selector, sample_number)
