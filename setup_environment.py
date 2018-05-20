import os


os.environ['EPICS_CAS_AUTO_BEACON_ADDR_LIST'] = 'no'
os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'no'
os.environ['EPICS_CAS_BEACON_ADDR_LIST'] = '0.0.0.0'
os.environ['EPICS_CA_ADDR_LIST'] = '0.0.0.0'