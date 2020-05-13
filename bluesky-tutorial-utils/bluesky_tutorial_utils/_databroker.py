from pathlib import Path

import appdirs
from event_model import RunRouter
import intake
from suitcase.msgpack import Serializer


def setup_data_saving(RE):
    """
    Subscribe a suitcase Serializer to RE and return a corresponding Catalog.

    The format happens to be msgpack, but that should be treated as an
    implementation detail subject to change.
    """
    directory = appdirs.user_data_dir("bluesky", "tutorial_utils")
    driver = intake.registry["bluesky-msgpack-catalog"]
    catalog = driver(str(Path(directory, "*.msgpack")))

    class PatchedSerializer(Serializer):
        """
        Work around https://github.com/bluesky/databroker/pull/559
        """

        def stop(self, doc):
            super().stop(doc)
            catalog.force_reload()

    def factory(name, start):
        return [PatchedSerializer(directory)], []

    rr = RunRouter([factory])
    RE.subscribe(rr)
    return catalog
