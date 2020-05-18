from pathlib import Path

import numpy as np

from bluesky import RunEngine
from bluesky.plans import count
from bluesky.preprocessors import SupplementalData
import bluesky.plans as bp
from databroker.utils import normalize_human_friendly_time
import event_model
import tzlocal

from ._newton import NewtonSimulator

here = Path(__file__).parent


class RewriteTimes(event_model.SingleRunDocumentRouter):
    def __init__(self, t0, callback):
        self._callback = callback
        self._t0 = normalize_human_friendly_time(t0, tzlocal.get_localzone().zone)
        self._delta = None
        super().__init__()

    def __call__(self, name, doc):
        # Emit the modified document to self._callback.
        name, doc = super().__call__(name, doc)
        self._callback(name, doc)

    def _patch_time(self, doc):
        doc = doc.copy()
        doc["time"] -= self._delta
        return doc

    def _patch_time_stamps(self, ts_dict):
        return {k: v - self._delta for k, v in ts_dict.items()}

    def start(self, doc):
        self._delta = doc["time"] - self._t0
        return self._patch_time(doc)

    def descriptor(self, doc):
        return self._patch_time(doc)

    def stop(self, doc):
        return self._patch_time(doc)

    def event(self, doc):
        doc = self._patch_time(doc)
        doc["timestamps"] = self._patch_time_stamps(doc["timestamps"])
        return doc

    def event_page(self, doc):
        return self._patch_time(doc)


def generate_example_data(callback):
    from ophyd.sim import det, motor1, motor2, motor3
    motor1.set(3.1).wait()
    motor2.set(-1000.02).wait()
    motor3.set(5.01).wait()

    RE = RunEngine()
    sd = SupplementalData(baseline=[motor1, motor2, motor3])
    RE.preprocessors.append(sd)

    RE.md["operator"] = "Dmitri"
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-01-01 9:00", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-01-01 9:05", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-01-01 9:07", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-02-01 9:00", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-02-01 9:05", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-02-01 13:00", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-02-01 15:00", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-02-01 15:05", callback))
    RE(
        count([det], 5, delay=0.05),
        RewriteTimes("2020-02-01 15:07", callback),
        operator="Michael",
    )
    RE(
        count([det], 5, delay=0.05),
        RewriteTimes("2020-02-01 15:08", callback),
        operator="Michael",
    )
    _generate_newton_data(
        RE,
        callback,
        [
            "2020-02-02 9:00",
            "2020-02-02 10:00",
            "2020-02-02 12:00",
            "2020-02-02 13:00",
            "2020-02-02 15:00",
            "2020-02-02 17:00",
            "2020-02-02 19:00",
        ],
    )


def _generate_newton_data(RE, callback, time_vector, **kwargs):
    ns = NewtonSimulator(50, 2 * np.pi / 0.4, name='ns')

    for ts in time_vector:
        RE(bp.scan([ns], ns.gap, 0, 4, 25), RewriteTimes(ts, callback), **kwargs)


directory = here / "example_data"


def save_example_data():
    """
    Run this from repo root to re-generate data.

    python -c "import bluesky_tutorial_utils; bluesky_tutorial_utils.save_example_data()"
    """
    import suitcase.jsonl

    def factory(name, doc):
        return [suitcase.jsonl.Serializer(str(directory))], []

    rr = event_model.RunRouter([factory])
    generate_example_data(rr)


def get_example_catalog():
    from databroker._drivers.jsonl import BlueskyJSONLCatalog

    # TODO Use pkg_resources here. This relies on this being an editable
    # installation.
    return BlueskyJSONLCatalog(str(directory / "*.jsonl"))
