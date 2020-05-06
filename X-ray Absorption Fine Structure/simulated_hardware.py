from glob import glob
from pathlib import Path

import numpy
from ophyd.sim import SynSignal, SynAxis
import pandas


for filename in glob(str(Path(__file__).parent / "data" / "pitch_vs_I0" / "*.csv")):
    # Grab the first file. Maybe later take a random one.
    # Each one is at a different energy, so it would not make sense to concat them.
    data = pandas.read_csv(filename)
    break


def compute_I0():
    return numpy.interp(pitch.readback.get(), data["dcm_pitch"], data["I0"])


pitch = SynAxis(name="pitch")
pitch.set(4).wait()  # initialize at a reasonable value
# pitch.delay = 0.05  # to simulate movement time
I0 = SynSignal(name="I0", func=compute_I0)
