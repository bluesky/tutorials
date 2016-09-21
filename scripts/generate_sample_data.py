import os
import tzlocal
from bluesky import RunEngine
from bluesky.plans import scan, count, relative_scan
from bluesky.examples import det, motor, det1, det2, motor1, motor2, flyer1


def make_broker(dirname):
    from portable_mds.sqlite.mds import MDS
    from portable_fs.sqlite.fs import FileStore
    from databroker import Broker

    mds = MDS({'directory': dirname,
               'timezone': tzlocal.get_localzone().zone})
    fs = FileStore({'dbpath': os.path.join(dirname, 'filestore.db')})
    return Broker(mds, fs)


def generate_data(RE):
    # This adds {'proposal_id': 1} to all future runs, unless overridden.
    RE.md['proposal_id'] = 1
    RE(count([det]))
    RE(scan([det], motor, 1, 5, 5))
    RE(scan([det], motor, 1, 10, 10))

    RE.md['proposal_id'] = 2
    RE(count([det]))
    RE(scan([det], motor, -1, 1, 5))
    RE(relative_scan([det], motor, 1, 10, 10))
    RE(scan([det], motor, -1, 1, 1000))

    RE.md['proposal_id'] = 3
    # This adds {'operator': 'Ken'} to all future runs, unless overridden.
    RE.md['operator'] = 'Ken'
    RE(count([det]), purpose='calibration', sample='A')
    RE(scan([det], motor, 1, 10, 10), operator='Dan')  # temporarily overrides Ken
    RE(count([det]), sample='A')  # (now back to Ken)
    RE(count([det]), sample='B')
    RE.md['operator'] = 'Dan'
    RE(count([det]), purpose='calibration')
    RE(scan([det], motor, 1, 10, 10))
    del RE.md['operator']  # clean up by un-setting operator


if __name__ == '__main__':
    db = make_broker(os.path.expanduser('~/.data-cache/'))
    RE = RunEngine({})
    RE.subscribe('all', db.mds.insert)
    generate_data(RE)
