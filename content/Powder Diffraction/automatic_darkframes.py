import bluesky.plan_stubs as bps
import bluesky_darkframes
from simulated_hardware import detector, shutter

def dark_plan(detector):
    # Restage to ensure that dark frames goes into a separate file.
    yield from bps.unstage(detector)
    yield from bps.stage(detector)
    yield from bps.mv(shutter, 'closed')
    # The `group` parameter passed to trigger MUST start with
    # bluesky-darkframes-trigger.
    yield from bps.trigger(detector, group='bluesky-darkframes-trigger')
    yield from bps.wait('bluesky-darkframes-trigger')
    snapshot = bluesky_darkframes.SnapshotDevice(detector)
    yield from bps.mv(shutter, 'open')
    # Restage.
    yield from bps.unstage(detector)
    yield from bps.stage(detector)
    return snapshot

def setup_automatic_darkframes(RE):
    # Take a fresh dark frame if the last one we took *with this exposure time*
    # is more than 30 seconds old.
    dark_frame_preprocessor = bluesky_darkframes.DarkFramePreprocessor(
        dark_plan=dark_plan, detector=detector, max_age=30,
        locked_signals=[detector.exposure_time])
    RE.preprocessors.append(dark_frame_preprocessor)
    return dark_frame_preprocessor