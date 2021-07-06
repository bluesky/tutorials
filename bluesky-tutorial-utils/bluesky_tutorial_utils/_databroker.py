def setup_data_saving(RE):
    """
    Subscribe a suitcase Serializer to RE and return a corresponding Catalog.

    The format happens to be msgpack, but that should be treated as an
    implementation detail subject to change.
    """
    import appdirs
    from event_model import RunRouter
    import intake
    from suitcase.msgpack import Serializer
    from pathlib import Path

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


def setup_data_saving_future_version(RE):
    from tiled.client import from_catalog
    from suitcase.mongo_normalized import Serializer
    from databroker.mongo_normalized import Catalog

    # Make a transient Catalog backed by mongomock.
    catalog = Catalog.from_mongomock()
    # TODO Serializer should accept just one database; the only
    # reason to need two is for old NSLS-II deployments that put
    # Resource and Datum documents in a separate datbase from the rest.
    serializer = Serializer(catalog.database, catalog.database)
    # Send documents from RE to this Catalog.
    RE.subscribe(serializer)
    # Construct a client-side Catalog for the service-side Catalog.
    client = from_catalog(catalog)
    return client
