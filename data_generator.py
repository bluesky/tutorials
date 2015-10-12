from bluesky.examples import motor, det
from bluesky.standard_config import gs
from bluesky.scans import AbsScan


gs.RE.md['owner'] = 'demo'
gs.RE.md['group'] = 'demo'
gs.RE.md['config'] = {}
gs.RE.md['beamline_id'] = 'demo'


scan = AbsScan([det], motor, 1, 5, 5)
gs.RE(scan, mood='optimisitc')
