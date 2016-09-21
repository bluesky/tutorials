import os
import tzlocal
from portable_mds.sqlite.mds import MDS
from portable_fs.sqlite.fs import FileStore
from databroker import Broker


def make_broker(dirname):
    mds = MDS({'directory': dirname,
               'timezone': tzlocal.get_localzone().zone})
    fs = FileStore({'dbpath': os.path.join(dirname, 'filestore.db')})
    return Broker(mds, fs)


if __name__ == '__main__':
    db = make_broker(os.path.expanduser('~/.data-cache/'))
