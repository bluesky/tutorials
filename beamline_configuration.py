import os

# Set some enviornment variables before importing pyepics.
os.environ['EPICS_CAS_AUTO_BEACON_ADDR_LIST'] = 'no'
os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'no'
os.environ['EPICS_CAS_BEACON_ADDR_LIST'] = '0.0.0.0'
os.environ['EPICS_CA_ADDR_LIST'] = '0.0.0.0'

import matplotlib
matplotlib.use('nbAgg')  # i.e. %matplotlib notebook

import nslsii
from ophyd import Device, Component, EpicsSignal
from ophyd.signal import EpicsSignalBase
from ophyd.areadetector.filestore_mixins import resource_factory
import uuid
import os
from pathlib import Path
import numpy as np
from IPython import get_ipython

try:
    del RE
except NameError:
    pass
nslsii.configure_base(get_ipython().user_ns, 'temp', epics_context=False)


class Det(Device):
    det = Component(EpicsSignal, ':det', kind='hinted')
    exp = Component(EpicsSignal, ':exp', kind='config')

# here there be 🐉🐉🐉🐉🐉🐉


class ArraySignal(EpicsSignalBase):
    def __init__(self, read_pv, **kwargs):
        super().__init__(read_pv, **kwargs)
        cl = self.cl
        base_pv, _ = read_pv.rsplit(':', maxsplit=1)
        self._size_pv = cl.get_pv(
            ':'.join((base_pv, 'ArraySize_RBV')))

        self._last_ret = None
        self._asset_docs_cache = []

    def trigger(self):
        os.makedirs('/tmp/demo', exist_ok=True)
        st = super().trigger()
        ret = super().read()
        val = ret[self.name]['value'].reshape(self._size_pv.get())

        resource, datum_factory = resource_factory(
            spec='npy',
            root='/tmp',
            resource_path=f'demo/{uuid.uuid4()}.npy',
            resource_kwargs={},
            path_semantics='posix')
        datum = datum_factory({})
        self._asset_docs_cache.append(('resource', resource))
        self._asset_docs_cache.append(('datum', datum))
        fpath = Path(resource['root']) / resource['resource_path']
        np.save(fpath, val)

        ret[self.name]['value'] = datum['datum_id']
        self._last_ret = ret
        return st

    def describe(self):
        ret = super().describe()
        ret[self.name]['shape'] = [int(k)
                                   for k in
                                   self._size_pv.get()]
        ret[self.name]['external'] = 'FILESTORE:'
        del ret[self.name]['upper_ctrl_limit']
        del ret[self.name]['lower_ctrl_limit']
        return ret

    def read(self):
        if self._last_ret is None:
            raise Exception('read before being triggered')
        return self._last_ret

    def collect_asset_docs(self):
        items = list(self._asset_docs_cache)
        self._asset_docs_cache.clear()
        for item in items:
            yield item


class Spot(Device):
    img = Component(ArraySignal, ':det')
    roi = Component(EpicsSignal, ':img_sum', kind='hinted')
    exp = Component(EpicsSignal, ':exp', kind='config')

    def collect_asset_docs(self):
        yield from self.img.collect_asset_docs()

    def trigger(self):
        return self.img.trigger()


ph = Det('jitter_read:ph', name='ph')
edge = Det('jitter_read:edge', name='edge')
slit = Det('jitter_read:slit', name='slit')

motor_ph = EpicsSignal('jitter_read:ph:mtr',
                       name='motor_ph')
motor_edge = EpicsSignal('jitter_read:edge:mtr',
                         name='motor_edge')
motor_slit = EpicsSignal('jitter_read:slit:mtr',
                         name='motor_slit')

spot = Spot('jitter_read:dot', name='spot')
mtr_spotx = EpicsSignal('jitter_read:dot:mtrx',
                        name='motor_spotx')
mtr_spoty = EpicsSignal('jitter_read:dot:mtry',
                        name='motor_spoty')

I = EpicsSignal('jitter_read:current', name='I')
