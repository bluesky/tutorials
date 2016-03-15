from bluesky.examples import motor, det
# Note: importing from standard_config raises a qt/mpl-related error.
from bluesky.global_state import gs
from bluesky.register_mds import register_mds
from bluesky.plans import AbsScanPlan


register_mds(gs.RE)
gs.RE.md['owner'] = 'demo'
gs.RE.md['group'] = 'demo'
gs.RE.md['config'] = {}
gs.RE.md['beamline_id'] = 'demo'


scan = AbsScanPlan([det], motor, 1, 5, 5)
gs.RE(scan, mood='optimistic')
