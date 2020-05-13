import pathlib
import requests
import subprocess
import sys


def rsoxs_simulation_data(dest="rsoxs_simulation_data"):
    """
    Download and decompress dataset unless destination already exists.

    Return False if destination exists and there is nothing to do, True otherwise.
    """
    if pathlib.Path(dest).exists():
        return False
    # URL is a world-viewable link to
    # https://www.dropbox.com/home/DAMA/Conferences%20%26%20Meetings/FY2020/NSLS-II%20%26%20CFN%20Users'%20meeting%20(May%202020)/200513_xArray/nxs
    print("Downloading...", file=sys.stderr)
    URL = "https://www.dropbox.com/sh/lkypngc3aokxx05/AAClQpX5IH3z3wWRj93iCOola?dl=0"
    subprocess.run(["wget", URL, "-O", "rsoxs_simulation_data.zip"])
    print("Extracting...", file=sys.stderr)
    subprocess.run(["unzip", "rsoxs_simulation_data.zip", "-d", dest])
    return True
