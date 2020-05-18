from bluesky.plan_stubs import mv
from bluesky.plans import rel_scan
from bluesky.preprocessors import subs_decorator
from bluesky.callbacks.mpl_plotting import LivePlot
from lmfit.models import SkewedGaussianModel
import pandas, numpy
from scipy.ndimage import center_of_mass
import matplotlib.pyplot as plt

from databroker.core import SingleRunCache

from simulated_hardware import pitch, I0


def com(signal):
    """Return the center of mass of a 1D array. This is used to find the
    center of rocking curve scans."""
    return int(round(center_of_mass(signal)[0]))

def peak(signal):
    """Return the index of the maximum of a 1D array. This is used to find the
    peak position of rocking curve scans."""
    return pandas.Series.idxmax(signal)


def rocking_curve(start=-0.10, stop=0.10, nsteps=101, choice="peak"):
    """Perform a relative scan of the DCM 2nd crystal pitch around the current
    position to find the peak of the crystal rocking curve.  Begin by opening
    the hutch slits to 3 mm. At the end, move to the position of maximum
    intensity on I0, then return to the hutch slits to their original height.
    Input:
      start:    (float)  starting position relative to current  [-0.1]
      end:      (float)  ending position relative to current    [0.1]
      nsteps:   (int)    number of steps                        [101]
      choice:   (string) 'peak', fit' or 'com' (center of mass) ['peak']
    If choice is fit, the fit is performed using the
    SkewedGaussianModel from lmfit, which works pretty well for this
    measurement at BMM.  The line shape is a bit skewed due to the
    convolution with the slightly misaligned entrance slits.
    """

    # Cache the data here as it is collected so we can examine it here and use
    # it to make decisions.
    src = SingleRunCache()

    @subs_decorator(LivePlot("I0", pitch.name, ax=plt.gca()))
    @subs_decorator(src.callback)
    def scan_dcm_pitch():
        line1 = "%s, %s, %.3f, %.3f, %d -- starting at %.3f\n" % (
            pitch.name,
            "I0",
            start,
            stop,
            nsteps,
            pitch.readback.get(),
        )
        uid = yield from rel_scan([I0], pitch, start, stop, nsteps)

        # The data that we just acquired has been cached in memory by src.
        # Access it as a pandas DataFrame so that we can conveniently do some
        # math on it.
        run = src.retrieve()
        t = run.primary.read().to_dataframe()
        if choice.lower() == "com":
            signal = numpy.array(t["I0"])
            position = com(signal)
            top = t['pitch'].iloc[position]
        elif choice.lower() == "fit":
            signal = numpy.array(t["I0"])
            pitch_ = numpy.array(t["pitch"])
            mod = SkewedGaussianModel()
            pars = mod.guess(signal, x=pitch_)
            out = mod.fit(signal, pars, x=pitch_)
            print(out.fit_report(min_correl=0))
            out.plot()
            top = out.params["center"].value
        else:
            signal = t['I0']
            position = peak(signal)
            top = t[pitch.name][position]

        print(
            "rocking curve scan: %s\tuid = %s, scan_id = %d"
            % (line1, uid, run.metadata["start"]["scan_id"])
        )
        print(f"Found and moved to peak at {top:.3} via method {choice}")
        yield from mv(pitch, top)

    yield from scan_dcm_pitch()
