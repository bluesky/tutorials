

from bluesky import RunEngine
from bluesky.utils import PersistentDict

from pathlib import Path

RE = RunEngine({})
RE.md = PersistentDict(str(Path("~/.bluesky_history").expanduser()))

from bluesky import SupplementalData
sd = SupplementalData()
RE.preprocessors.append(sd)

# Set up a Broker.
from databroker import Broker
db = Broker.named("temp")
# and subscribe it to the RunEngine
RE.subscribe(db.insert)


from bluesky.magics import BlueskyMagics
get_ipython().register_magics(BlueskyMagics)


# Use BestEffortCallback 
# TODO: Retire our use of BestEffortCallback, using a table from
# bluesky_widgets once one is available.
from bluesky.callbacks.best_effort import BestEffortCallback
bec = BestEffortCallback()
#bec.disable_plots()
RE.subscribe(bec)


import matplotlib.pyplot as plt
# Make plots update live while scans run.
from bluesky.utils import install_nb_kicker
install_nb_kicker()

# convenience imports
# some of the * imports are for 'back-compatibility' of a sort -- we have
# taught BL staff to expect LiveTable and LivePlot etc. to be in their
# namespace
import numpy as np

import bluesky.callbacks
from bluesky.callbacks import *

import bluesky.plans
import bluesky.plans as bp
from bluesky.plans import *

import bluesky.plan_stubs
import bluesky.plan_stubs as bps
from bluesky.plan_stubs import *

import bluesky.preprocessors
import bluesky.preprocessors as bpp
# import bluesky.simulators
# from bluesky.simulators import *

from bluesky.simulators import summarize_plan, check_limits, plot_raster_path
#from bluesky.plan_tools import plot_raster_path

from ophyd.sim import det, motor, noisy_det

### make temperature motor alias
from ophyd.sim import motor3 as temperature
temperature.name = "temperature"

# from bluesky.utils import ProgressBarManager
# RE.waiting_hook = ProgressBarManager()