import pathlib
import datetime
import six
import h5py
import warnings
import numpy as np
import pandas as pd
import xarray as xr
import dask


def initNexus(fileName,simulation_variables=None,overwrite=False):
    timestamp = "T".join( str( datetime.datetime.now() ).split() )
    
    fileName = pathlib.Path(fileName)
    if fileName.exists() and (not overwrite):
        raise FileExistsError('Pass overwrite=True to enable overwriting the existing file.')

    # create the HDF5 NeXus file
    with h5py.File(fileName, "w") as f:
        # point to the default data to be plotted
        f.attrs[u'default']          = u'entry'
        # give the HDF5 root some more attributes
        f.attrs[u'file_name']        = str(fileName.parts[-1])
        f.attrs[u'file_time']        = timestamp
        f.attrs[u'instrument']       = u'CyRSoXS v' #@TODO: learn the CyRSoXS version stamp and embed here
        f.attrs[u'creator']          = u'CyRSoXS output packager'
        f.attrs[u'NeXus_version']    = u'4.3.0'
        f.attrs[u'HDF5_version']     = six.u(h5py.version.hdf5_version)
        f.attrs[u'h5py_version']     = six.u(h5py.version.version)

        # create the NXentry group
        nxentry = f.create_group(u'entry')
        nxentry.attrs[u'NX_class'] = u'NXentry'
        nxentry.attrs[u'canSAS_class'] = u'SASentry'
        nxentry.attrs[u'default'] = u'data'
        nxentry.create_dataset(u'title', data=u'SIMULATION NAME GOES HERE') #@TODO
              
        # create the NXinstrument metadata group
        nxinstr = nxentry.create_group(u'instrument')
        nxinstr.attrs[u'NX_class'] = u'NXinstrument'
        nxinstr.attrs[u'canSAS_class'] = u'SASinstrument'

        nxprocess = nxinstr.create_group(u'simulation_engine')
        nxprocess.attrs[u'NX_class'] = u'NXprocess'
        nxprocess.attrs[u'canSAS_class'] = u'SASprocess'
        nxprocess.attrs[u'name'] = u'CyRSoXS Simulation Engine'
        nxprocess.attrs[u'date'] = timestamp # @TODO: get timestamp from simulation run and embed here.
        nxprocess.attrs[u'description'] = u'Simulation of RSoXS pattern from optical constants del/beta and morphology'

        sim_notes = nxprocess.create_group(u'notes')
        sim_notes.attrs[u'NX_class'] = u'NXnote'

        sim_notes.attrs[u'description'] = u'Simulation Engine Input Parameters/Run Data'
        sim_notes.attrs[u'author'] = u'CyRSoXS PostProcessor'
        sim_notes.attrs[u'data'] = u'Run metadata goes here' #@TODO
        
        if simulation_variables is not None:
            for key,value in simulation_variables.items():
                if 'energy' in key.lower():
                    units = u'eV'
                elif 'angle' in key.lower():
                    units = u'degree'
                elif 'physsize' in key.lower():
                    units = u'nm' #@TODO: is this correct?
                else:
                    units = u''
    
                metads = sim_notes.create_dataset(key,data=value)
                metads.attrs[u'units'] = units
        nxsample = nxentry.create_group(u'sample')
        nxsample.attrs[u'NX_class'] = u'NXsample'
        nxsample.attrs[u'canSAS_class'] = u'SASsample'
        
        nxsample.attrs[u'name'] = 'SAMPLE NAME GOES HERE'
        nxsample.attrs[u'description'] = 'SAMPLE DESCRIPTION GOES HERE'
        nxsample.attrs[u'type'] = 'simulated data'
        
        # #nxsample.create_dataset(u'component',['component 1','component 2'])
        # optics = nxsample.create_group(u'optical_constants')
        # comp = optics.create_group(u'component 1')
        # #comp.create_dataset

def checkFile(fileName,simulation_variables):
    if simulation_variables is None:
        warnings.warn('Cannot verify that .nxs matches data without simulation_variables defined.')
        
    with h5py.File(fileName, "r") as f:
        notes = f[u'entry/instrument/simulation_engine/notes']
        for key,value in simulation_variables.items():
            if key not in notes:
                raise ValueError(f'checkFile Failed! Simulation variable "{key}" not found in {fileName}')
            if notes[key][()]!=value:
                raise ValueError(f'checkFile Failed! Simulation variable {key}={value} doesn\'t match file value: {key}={notes[key][()]}')
                
        
def writeSingleImageQxQy(fileName,img,qx,qy,simulation_variables=None,group_name=u'sasdata_singleimg'):
    timestamp = "T".join( str( datetime.datetime.now() ).split() )
    
    fileName = pathlib.Path(fileName)
    if not fileName.exists():
        initNexus(fileName,simulation_variables)
        
    if simulation_variables is not None:
        checkFile(fileName,simulation_variables)

    # create the HDF5 NeXus file
    with h5py.File(fileName, "a") as f:
        #update the timestamp
        f.attrs[u'file_time']        = timestamp
        
        nxentry = f[u'entry']
            
        nxdata = nxentry.create_group(group_name)
        nxdata.attrs[u'NX_class'] = u'NXdata'
        nxdata.attrs[u'canSAS_class'] = u'SASdata'
        #nxdata.attrs[u'canSAS_version'] = u'0.1' #required for Nika to read the file.
        nxdata.attrs[u'signal'] = u'I'      # Y axis of default plot
        nxdata.attrs[u'I_axes'] = u'Qx,Qy'         # X axis of default plot
        nxdata.attrs[u'Q_indices'] = '[0,1]'   # use "mr" as the first dimension of I00

        # X axis data
        ds = nxdata.create_dataset(u'I', data=img)
        ds.attrs[u'units'] = u'arbitrary'
        ds.attrs[u'long_name'] = u'Simulated Intensity (arbitrary units)'    # suggested X axis plot label
        # the following are to enable compatibility with Nika canSAS loading
        ds.attrs[u'signal'] = 1
        #ds.attrs[u'axes'] = u'Qx,Qy'

        # Y axis data
        ds = nxdata.create_dataset(u'Qx', data=qx)
        ds.attrs[u'units'] = u'1/angstrom'
        ds.attrs[u'long_name'] = u'Qx (A^-1)'    # suggested Y axis plot label

        ds = nxdata.create_dataset(u'Qy', data=qy)
        ds.attrs[u'units'] = u'1/angstrom'
        ds.attrs[u'long_name'] = u'Qy (A^-1)'    # suggested Y axis plot label



def writeSingleImageChiQ(fileName,img,chi,q,simulation_variables=None,group_name=u'sasdata_singleimg_unwrap'):
    timestamp = "T".join( str( datetime.datetime.now() ).split() )
    
    fileName = pathlib.Path(fileName)
    if not fileName.exists():
        initNexus(fileName,simulation_variables)
        
    if simulation_variables is not None:
        checkFile(fileName,simulation_variables)

    # create the HDF5 NeXus file
    with h5py.File(fileName, "a") as f:
        #update the timestamp
        f.attrs[u'file_time']        = timestamp
        
        nxentry = f[u'entry']
            
        nxdata = nxentry.create_group(group_name)
        nxdata.attrs[u'NX_class'] = u'NXdata'
        nxdata.attrs[u'canSAS_class'] = u'SASdata'
        #nxdata.attrs[u'canSAS_version'] = u'0.1' #required for Nika to read the file.
        nxdata.attrs[u'signal'] = u'I'      # Y axis of default plot
        nxdata.attrs[u'I_axes'] = u'chi,Q'         # X axis of default plot
        nxdata.attrs[u'Q_indices'] = '[0,1]'   # use "mr" as the first dimension of I00

        # X axis data
        ds = nxdata.create_dataset(u'I', data=img)
        ds.attrs[u'units'] = u'arbitrary'
        ds.attrs[u'long_name'] = u'Simulated Intensity (arbitrary units)'    # suggested X axis plot label
        # the following are to enable compatibility with Nika canSAS loading
        ds.attrs[u'signal'] = 1
        #ds.attrs[u'axes'] = u'Qx,Qy'

        # Y axis data
        ds = nxdata.create_dataset(u'Q', data=q)
        ds.attrs[u'units'] = u'1/angstrom'
        ds.attrs[u'long_name'] = u'Q (A^-1)'    # suggested Y axis plot label
 
        ds = nxdata.create_dataset(u'chi', data=chi)
        ds.attrs[u'units'] = u'degree'
        ds.attrs[u'long_name'] = u'azimuthal angle chi (deg)'    # suggested Y axis plot label
        
def read_singleimg_nxs(fname,sasdata=u'',lazy=False):
    if sasdata:
        sasdata = 'sasdata_singleimg' + '_' + sasdata
    else:
        sasdata = 'sasdata_singleimg'
        
    
    h5 = h5py.File(fname,'r')
    if sasdata not in h5['entry']:
        raise ValueError(f'Single image sasdata "{sasdata}" not found in {fname}')
        
    signal_label = h5['entry'][sasdata].attrs['signal']
    if lazy:
        warnings.warn('Using delayed,lazy loading for intensity data. USER IS RESPONSIBLE FOR CLOSING THE H5 FILE.')
        signal = dask.array.from_array(h5['entry'][sasdata][signal_label])
    else:
        signal = h5['entry'][sasdata][signal_label][()]
    
    ylabel,xlabel = h5['entry'][sasdata].attrs['I_axes'].split(',')
    y = h5['entry'][sasdata][ylabel][()]
    x = h5['entry'][sasdata][xlabel][()]
     
    da= xr.DataArray(signal,
                     dims=[ylabel,xlabel],
                     coords={ylabel:y,xlabel:x},
                     name=signal_label,
                     )
    if lazy:
        da.attrs['lazy'] = True
        da.attrs['h5'] = h5
        return da
    else:
        da.attrs['lazy'] = False
        return da
        
def writeImageEnergySeries(fileName,da_image_list,energies,chi=False,simulation_variables=None,group_name_mod=u''):
    
    fileName = pathlib.Path(fileName)
    if not fileName.exists():
        initNexus(fileName,simulation_variables)
        
    if simulation_variables is not None:
        checkFile(fileName,simulation_variables)
    
    dataArray = xr.concat(da_image_list,dim='Energy').assign_coords(Energy=energies)

    # create the HDF5 NeXus file
    with h5py.File(fileName, "a") as f:
        timestamp = "T".join( str( datetime.datetime.now() ).split() )
        f.attrs[u'file_time'] = timestamp
        
        # create the NXdata group for I(Qx,Qy)
        nxentry = f[u'entry']
        nxdata = nxentry.create_group(u'sasdata_energyseries'+group_name_mod)
        nxdata.attrs[u'NX_class'] = u'NXdata'
        nxdata.attrs[u'canSAS_class'] = u'SASdata'
        nxdata.attrs[u'signal'] = u'I'      # Y axis of default plot
        nxdata.attrs[u'Q_indices'] = '[0,1]'   # use "mr" as the first dimension of I00
    
        data = np.swapaxes(np.swapaxes(dataArray.values,0,1),1,2)#move energy axis to end
        ds = nxdata.create_dataset(u'I', data=data,compression='gzip',compression_opts=9)
        ds.attrs[u'units'] = u'arbitrary'
        ds.attrs[u'long_name'] = u'Simulated Intensity (arbitrary units)'    # suggested X axis plot label
    
    
        if chi:
            nxdata.attrs[u'I_axes'] = u'chi,Q,E'         # X axis of default plot
            
            ds = nxdata.create_dataset(u'Q', data=dataArray.Q.values)
            ds.attrs[u'units'] = u'1/angstrom'
            ds.attrs[u'long_name'] = u'Q (A^-1)'    # suggested Y axis plot label

            ds = nxdata.create_dataset(u'chi', data=dataArray.Chi.values)
            ds.attrs[u'units'] = u'degree'
            ds.attrs[u'long_name'] = u'azimuthal angle chi (deg)'    # suggested Y axis plot labelk
        else:
            nxdata.attrs[u'I_axes'] = u'Qx,Qy,E'         # X axis of default plot
            
            ds = nxdata.create_dataset(u'Qx', data=dataArray.Qx.values)
            ds.attrs[u'units'] = u'1/angstrom'
            ds.attrs[u'long_name'] = u'Qx (A^-1)'    
        
            ds = nxdata.create_dataset(u'Qy', data=dataArray.Qy.values)
            ds.attrs[u'units'] = u'1/angstrom'
            ds.attrs[u'long_name'] = u'Qy (A^-1)'    

        ds = nxdata.create_dataset(u'E', data=dataArray.Energy.values)
        ds.attrs[u'units'] = u'eV'
        ds.attrs[u'long_name'] = u'Simulated Energy (eV)'    
        
def read_energyseries(fname,remesh=False,chi=False,lazy=False):
    if chi and remesh:
        raise ValueError('No remeshed chi stored in file.')
    elif chi:
        sasdata = 'sasdata_energyseries_chi' 
    elif remesh:
        sasdata = 'sasdata_energyseries_remesh' 
    else:
        sasdata = 'sasdata_energyseries' 
        
    h5 = h5py.File(fname,'r')
    if sasdata not in h5['entry']:
        raise ValueError(f'Single image sasdata "{sasdata}" not found in {fname}')
        
    signal_label = h5['entry'][sasdata].attrs['signal']
    if lazy:
        warnings.warn('Using delayed,lazy loading for intensity data. USER IS RESPONSIBLE FOR CLOSING THE H5 FILE.')
        signal = dask.array.from_array(h5['entry'][sasdata][signal_label])
    else:
        signal = h5['entry'][sasdata][signal_label][()]
    
    ylabel,xlabel,zlabel = h5['entry'][sasdata].attrs['I_axes'].split(',')
    z = h5['entry'][sasdata][zlabel][()]
    y = h5['entry'][sasdata][ylabel][()]
    x = h5['entry'][sasdata][xlabel][()]
     
    da= xr.DataArray(signal,
                     dims=[ylabel,xlabel,zlabel],
                     coords={ylabel:y,xlabel:x,zlabel:z},
                     name=signal_label,
                     )
    if lazy:
        da.attrs['lazy'] = True
        da.attrs['h5'] = h5
        return da
    else:
        da.attrs['lazy'] = False
        return da
            

def build_pandas_index(nxs_path,prog_bar=True):
    nxs_path = pathlib.Path(nxs_path)
    nxs_files = list(nxs_path.glob('*nxs'))
    
    if prog_bar:
        import ipywidgets
        progress = ipywidgets.IntProgress(0,0,len(nxs_files))
        display(progress)
    
    index_table = []
    for i,nxs_file in enumerate(nxs_files):
        if prog_bar:
            progress.value = i
        with h5py.File(nxs_file,'r') as nxs:
            notes = nxs[u'entry/instrument/simulation_engine/notes']
            config =  {k:v[()] for k,v in notes.items()}
            config['nxs'] = nxs_file
            index_table.append(config)
    return pd.DataFrame(index_table)
