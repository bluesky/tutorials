import os
import requests
import shutil
import zipfile

from ._databroker import setup_data_saving


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
        local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return local_filename


def _unpack_zip(file, dir_to_extract_to):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        files = zip_ref.filelist
        zip_ref.extractall(dir_to_extract_to)
    return files


def fetch_rsoxs_example_data(dir_to_extract_to=None):
    """Fetch RSoXS example data and return a list of unpacked files.
    """
    if dir_to_extract_to is None:
        dir_to_extract_to = os.getcwd()

    # Download a zip-archive with the *.nxs data files.
    url = 'https://www.dropbox.com/sh/8z5jzb4iu7o3unj/AADQUqm2_oGgIxRBC8uuO6XWa?dl=1'
    rsoxs_zip = _download_file(url, local_filename='rsoxs_data.zip')

    # Unpack it.
    files = _unpack_zip(rsoxs_zip, dir_to_extract_to)
    
    return files
