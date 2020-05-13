import pathlib
import requests
import shutil
import sys
import zipfile


def _download_file(url, local_filename=None):
    """Download a file from the provided url.

    Credit: https://stackoverflow.com/a/39217788/4143531.

    Parameters
    ----------
    url: str
        a download link to the file
    local_filename: str, optional
        a desired file name for the downloaded file

    Returns
    -------
    A name of the downloaded file
    """
    if local_filename is None:
        local_filename = url.split("/")[-1]
    with requests.get(url, stream=True) as r:
        with open(local_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    return local_filename


def _unpack_zip(file, dir_to_extract_to):
    with zipfile.ZipFile(file, "r") as zip_ref:
        files = zip_ref.filelist
        zip_ref.extractall(dir_to_extract_to)
    return files


def rsoxs_simulation_data(dest="rsoxs_simulation_data"):
    """
    Download and decompress dataset unless destination already exists.

    Return False if destination exists and there is nothing to do, True otherwise.
    """
    if pathlib.Path(dest).exists():
        return []
    # URL is a world-viewable link to
    # https://www.dropbox.com/home/DAMA/Conferences%20%26%20Meetings/FY2020/NSLS-II%20%26%20CFN%20Users'%20meeting%20(May%202020)/200513_xArray/nxs
    URL = "https://www.dropbox.com/sh/8z5jzb4iu7o3unj/AADQUqm2_oGgIxRBC8uuO6XWa?dl=1"

    # Download a zip-archive with the *.nxs data files.
    print("Downloading...", file=sys.stderr)
    rsoxs_zip = _download_file(URL, local_filename="rsoxs_simulation_data.zip")

    # Unpack it.
    print("Extracting...", file=sys.stderr)
    files = _unpack_zip(rsoxs_zip, dest)

    return files
