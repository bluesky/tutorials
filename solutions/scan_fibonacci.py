from bluesky.plans import list_scan

positions = [1, 1, 2, 3, 5, 8]
RE(list_scan([det], motor, positions))

# or, equivalently, without a separate variable:
RE(list_scan([det], motor, [1, 1, 2, 3, 5, 8]))
