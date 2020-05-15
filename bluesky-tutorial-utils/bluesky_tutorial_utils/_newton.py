"""Special use handler for training."""
import numpy as np
from ophyd import Device, Component as Cpt, Signal, DeviceStatus
from ophyd.device import Staged
from collections import deque
from event_model import compose_resource


def newton(gap, R, k):
    """
    Simulate Newton's Rings.

    Parameters
    ----------
    gap : float
        The closest distance between the sphere and the surface

    R : float
        Radius of the sphere

    k : float
        Wave number of the incoming light

    """
    X, Y = np.ogrid[-10:10:128j, -10:10:128j]
    d = np.hypot(X, Y)
    phi = ((gap + d * np.tan(np.pi / 2 - np.arcsin(d / R))) * 2) * k

    return 1 + np.cos(phi)


class NewtonHandler:
    """Class for simulating Newton's Rings on the fly as a handler."""

    specs = {"newton"}

    def __init__(self, filename, *, radius, wave_number):
        """
        Parameters
        ----------
        radius : float
            radius of the sphere

        wave_number : float
            The wave number of the incoming light.

        """
        self._R = radius
        self._k = wave_number

    def __call__(self, gap):
        """
        Parameters
        ----------
        gap : float
            The closest distance between the sphere and surface

        """
        return newton(gap, self._R, self._k)

    def get_file_list(self, datum_kwarg_gen):
        """
        Get the list of files this instance reads.

        This handler has no files :)

        Returns
        -------
        empty list

        """
        return []


class ExternalFileReference(Signal):
    """
    A pure software signal where a Device can stash a datum_id
    """

    def __init__(self, *args, shape, **kwargs):
        super().__init__(*args, **kwargs)
        self.shape = shape

    def describe(self):
        res = super().describe()
        res[self.name].update(
            dict(
                external="FILESTORE:",
                dtype="array",
                shape=self.shape,
                dims=("x", "y"),
            )
        )
        return res


class NewtonSimulator(Device):
    gap = Cpt(Signal, value=0, kind="hinted")
    image = Cpt(ExternalFileReference, kind="normal", shape=(128, 128))

    def __init__(self, R, k, **kwargs):
        super().__init__(**kwargs)
        self._R = R
        self._k = k
        self._asset_docs_cache = deque()

    def stage(self):
        self._resource, self._datum_factory, _ = compose_resource(
            start={"uid": "a lie"},
            spec="newton",
            root="/",
            resource_path="",
            resource_kwargs={"radius": self._R, "wave_number": self._k},
        )
        self._resource.pop("run_start")
        self._asset_docs_cache.append(("resource", self._resource))

        return super().stage()

    def unstage(self):
        self._resource = self._datum_factory = None
        return super().unstage()

    def trigger(self):
        if self._staged != Staged.yes:
            raise RuntimeError(
                "This device must be staged before being triggered"
            )
        st = DeviceStatus(self)
        gap = self.gap.get()
        datum = self._datum_factory(datum_kwargs={"gap": gap})
        self._asset_docs_cache.append(("datum", datum))
        self.image.put(datum["datum_id"])
        st.set_finished()
        return st

    def collect_asset_docs(self):
        items = list(self._asset_docs_cache)
        self._asset_docs_cache.clear()
        for item in items:
            yield item
