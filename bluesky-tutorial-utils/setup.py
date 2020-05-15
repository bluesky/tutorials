from setuptools import setup, find_packages


setup(
    name="bluesky-tutorial-utils",
    packages=find_packages(),
    install_requires=["appdirs", "ophyd", "numpy", "event-model"],
    entry_points={
        "databroker.handlers": [
            "npy = bluesky_tutorial_utils._old_handlers:NpyHandler",
            "npy_FRAMEWISE = bluesky_tutorial_utils._old_handlers:NpyFrameWise",
            "newton = bluesky_tutorial_utils._newton:NewtonHandler",
        ]
    },
)
