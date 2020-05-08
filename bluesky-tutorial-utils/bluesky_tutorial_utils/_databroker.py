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

    def factory(name, start):
        return [Serializer(directory)], []

    rr = RunRouter([factory])
    RE.subscribe(rr)
    driver = intake.registry["bluesky-msgpack-catalog"]
    return driver(str(Path(directory, "*.msgpack")))
