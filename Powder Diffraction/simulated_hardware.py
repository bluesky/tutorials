import threading

import numpy
import numpy as np
from ophyd import Component, Device, Signal, DeviceStatus
from bluesky.plan_stubs import mv

from generate_data import make_random_peaks, generate_flat_field, generate_image


_history = {"sample": [], "light": [], "image": []}
_time = {"state": 0.0}
LIMIT = 1_000_000


def time_travel(t):
    if t > LIMIT:
        raise ValueError(f"Cannot time travel past {LIMIT}")
    _time["state"] = t


def current_time():
    t = _time["state"]
    print("current time is", t)
    return t


class Shutter(Signal):
    def put(self, value):
        if value == "open":
            _history["light"].append((current_time(),))
        if value == "closed":
            (opened_time,) = _history["light"].pop()
            _history["light"].append((opened_time, current_time()))
        super().put(value)


class SampleSelector(Signal):
    def put(self, value):
        current_value = self.get()
        if current_value:
            (loaded_time,) = _history["sample"].pop()
            _history["sample"].append((loaded_time, current_time()))
        if value:
            _history["sample"].append((current_time(),))
            _history["image"].append(patterns[value])
        super().put(value)


shutter = Shutter(name="shutter", value="closed")
sample_selector = SampleSelector(name="sample_selector", value=0)


# Map samples to patterns.
SHAPE = (512, 512)
patterns = {}
x = numpy.linspace(0, 30, num=3001)
intensities = {}
for i in range(1, 5):
    intensity = make_random_peaks(x) * 1000
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
    # exposure_time = Component(Signal, value=1)
    image = Component(Signal, value=numpy.zeros(SHAPE))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def trigger(self):
        # Start with a flat field.
        arr = generate_flat_field(SHAPE)
        f = make_illumination_combinations(
            _history["sample"], _history["image"], _history["light"], 1
        )
        arr = f(current_time())
        self.image.set(arr)
        READOUT_TIME = 0.017
        return TimerStatus(self, READOUT_TIME)

    def collect_asset_docs(self):
        yield from []


detector = DiffractionDetector(name="detector")


def make_decay_func(I0, a=10, t1=2, t2=10):
    def decay_func(x):
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            pre = np.nan_to_num(I0 ** 2 / a * np.exp(-(a * x / I0)))

            f1 = np.heaviside(t1 - t2, 1) * np.heaviside(x - t2, 1)
            f1a = np.exp(a * t2 / I0) - np.exp(a * x / I0)
            f1b = (np.exp(x * a / I0) - np.exp(a * t1 / I0)) * np.heaviside(-t1 + x, 1)
            f1 *= f1a + f1b

            f2 = np.heaviside(t2 - t1, 1) * np.heaviside(x - t1, 1)
            f2a = np.exp(t1 * a / I0) - np.exp(x * a / I0)
            f2b = (np.exp(x * a / I0) - np.exp(t2 * a / I0)) * np.heaviside(x - t2, 1)
            f2 *= f2a + f2b

        return np.nan_to_num(pre * (f1 - f2))

    return decay_func


def make_illumination_combinations(
    sample_history, im_history, light_history, a, tmax=LIMIT
):
    sample_history = sample_history.copy()
    im_history = im_history.copy()
    light_history = light_history.copy()
    decay_func_list = []

    if len(sample_history[-1]) == 1:
        sample_history[-1] = (sample_history[-1][0], tmax)
        # print ('setting max time to sample_history '+str(sample_history[-1]))

    if len(light_history[-1]) == 1:
        light_history[-1] = (light_history[-1][0], tmax)

    for i in range(len(sample_history)):
        this_im = im_history[i]
        # make a series of tuples
        im_tstart = sample_history[i][0]
        im_tend = sample_history[i][1]

        my_list = []
        # see if a time exists in a light_loop
        for j in range(len(light_history)):
            light_tstart = light_history[j][0]  # light on
            light_tend = light_history[j][1]  # light off

            # first, check if image ends before light starts
            if light_tstart > im_tend or light_tend < im_tstart:
                # print ('this light does not overlap sample')
                pass
            else:  # have some overlap
                # determine start
                use_start = im_tstart
                if im_tstart < light_tstart:
                    use_start = light_tstart
                use_end = im_tend
                if im_tend > light_tend:
                    use_end = light_tend
                my_list.append((use_start, use_end))

        for k in range(len(my_list)):
            # make a decay func for these
            decay_func_list.append(
                make_decay_func(this_im, a=a, t1=my_list[k][0], t2=my_list[k][1])
            )

    def f(t):
        return sum(f(t) for f in decay_func_list)

    return f


def load_sample(i):
    yield from mv(sample_selector, i)


def unload_sample():
    yield from mv(sample_selector, 0)


def light(state):
    "state: True or False"
    yield from mv(shutter, {True: "open", False: "closed"}[bool(state)])
