# Set up a databroker aimed at the hidden directory ~/.data-cache.
import os
import tzlocal
from portable_mds.sqlite.mds import MDS
from portable_fs.sqlite.fs import FileStore
from databroker import Broker

dirname = os.path.expanduser('~/.data-cache/')
mds = MDS({'directory': dirname,
            'timezone': tzlocal.get_localzone().zone})
fs = FileStore({'dbpath': os.path.join(dirname, 'filestore.db')})
db = Broker(mds, fs)
del dirname, mds, fs, MDS, FileStore, Broker, tzlocal  # clean up namespace

# Subscribe metadatastore to documents.
# If this is removed, data is not saved to metadatastore.
from bluesky.global_state import gs
gs.RE.subscribe('all', db.mds.insert)

# Import matplotlib and put it in interactive mode.
import matplotlib.pyplot as plt
plt.ion()

# Make plots live-update while scans run.
from bluesky.utils import install_nb_kicker
install_nb_kicker()
del install_nb_kicker

# For convenience, import some commonly-used functions and modules.
from bluesky.callbacks import *
from bluesky.spec_api import *
import bluesky.plans as bp
import time
import os
