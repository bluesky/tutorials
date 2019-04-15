def coarse_and_fine(detectors, motor, start, stop):
    yield from scan(detectors, motor, start, stop, 5)
    yield from scan(detectors, motor, start, stop, 30)

RE(coarse_and_fine([det], motor, -10, 10))
