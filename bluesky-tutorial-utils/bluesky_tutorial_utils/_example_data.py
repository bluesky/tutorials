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
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-01-01 9:00", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-01-01 9:05", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-01-01 9:07", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-02-01 9:00", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-02-01 9:05", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-02-01 13:00", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-02-01 15:00", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-02-01 15:05", callback))
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-02-01 15:07", callback), operator="Michael")
    RE(count([det], 5, delay=0.05), RewriteTimes("2020-02-01 15:08", callback), operator="Michael")


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
    return BlueskyJSONLCatalog(str(directory / "*.jsonl"))
