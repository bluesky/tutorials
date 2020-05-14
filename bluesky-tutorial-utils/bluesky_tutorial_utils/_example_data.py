from pathlib import Path

from bluesky import RunEngine
from bluesky.plans import count
from databroker.utils import normalize_human_friendly_time
import event_model
from ophyd.sim import det
import tzlocal


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

    def start(self, doc):
        self._delta = doc["time"] - self._t0
        return self._patch_time(doc)

    def descriptor(self, doc):
        return self._patch_time(doc)

    def stop(self, doc):
        return self._patch_time(doc)

    def event(self, doc):
        return self._patch_time(doc)

    def event_page(self, doc):
        return self._patch_time(doc)


def generate_example_data(callback):
    RE = RunEngine()
    RE.md["operator"] = "Dmitri"
    RE(count([det], 5, delay=0.1), RewriteTimes("2020-01-01", callback))
