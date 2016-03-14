# Copyright (c) Jupyter Development Team.
FROM jupyter/minimal-notebook

MAINTAINER NSLS-II <https://nsls-ii.github.io>

USER root

# Install and start mongo
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-key 7F0CEB10

RUN echo "deb http://repo.mongodb.org/apt/debian wheezy/mongodb-org/3.0 main" | tee /etc/apt/sources.list.d/mongodb-org-3.0.list
RUN apt-get update
RUN apt-get install -y mongodb-org
RUN mkdir -p /data/db
# Install the EPICS stack
#RUN apt-get install -yq wget
RUN wget --quiet http://epics.nsls2.bnl.gov/debian/repo-key.pub -O - | apt-key add -
RUN echo "deb http://epics.nsls2.bnl.gov/debian/ jessie/staging main contrib" | tee /etc/apt/sources.list.d/nsls2.list
RUN apt-get update
RUN apt-get install -yq build-essential git epics-dev epics-synapps-dev epics-iocstats-dev 
RUN apt-get install -yq procserv telnet
# get areadetector dependencies
RUN apt-get install -yq libhdf5-dev libx11-dev libxext-dev libxml2-dev libpng12-dev libbz2-dev libfreetype6-dev

USER jovyan

# Install Python 3 packages
RUN conda install --yes \
    'python=3.5*' \
    'ipywidgets=4.1*' \
    'pandas=0.17*' \
    'matplotlib=1.5*' \
    'scipy=0.17*' \
    'seaborn=0.7*' \
    'scikit-learn=0.17*' \
    'scikit-image=0.11*' \
    'sympy=0.7*' \
    'cython=0.23*' \
    'patsy=0.4*' \
    'statsmodels=0.6*' \
    'cloudpickle=0.1*' \
    'dill=0.2*' \
    'numba=0.23*' \
    'bokeh=0.11*' \
    'h5py=2.5*' \
    'pymongo' \
    'cytoolz' \
    && conda clean -yt


# pip install things not yet on lightsource2 channel.
RUN conda install --yes pip
RUN pip install boltons tzlocal
# dependency dragged in from (at least) ophyd.commands
RUN pip install prettytable
RUN pip install https://github.com/Nikea/historydict/zipball/master#egg=historydict
RUN pip install https://github.com/NSLS-II/bluesky/zipball/master#egg=bluesky
RUN pip install https://github.com/NSLS-II/doct/zipball/master#egg=doct
RUN pip install https://github.com/NSLS-II/metadatastore/zipball/master#egg=metadatastore
RUN pip install https://github.com/NSLS-II/filestore/zipball/master#egg=filestore
RUN pip install https://github.com/soft-matter/pims/zipball/master#egg=pims
RUN pip install https://github.com/nsls-ii/pyepics/zipball/master#egg=pyepics
RUN pip install https://github.com/nsls-ii/ophyd/zipball/master#egg=ophyd
RUN pip install https://github.com/NSLS-II/databroker/zipball/master#egg=databroker

# fix for 'missing PC' symbol, readline bug
RUN conda install -c lightsource2 --yes readline && conda clean -yt

# Configure MDS and FS connection parameters.
ENV MDS_HOST 127.0.0.1
ENV MDS_DATABASE demo-mds
ENV MDS_TIMEZONE US/Eastern
ENV MDS_PORT 27017
ENV FS_HOST 127.0.0.1
ENV FS_DATABASE demo-fs
ENV FS_PORT 27017

# clone and build EPICS device simulation code
USER root

RUN mkdir /epics && mkdir /epics/iocs
RUN mkdir /epics/src
RUN git clone https://github.com/dchabot/areadetector-1-9-1.git /epics/src/areadetector-1-9-1
RUN cd /epics/src/areadetector-1-9-1 && make -s all

RUN git clone https://github.com/dchabot/simioc.git /epics/iocs/simioc
RUN cd /epics/iocs/simioc && make -s all

# Install Jupyter server extensions.
USER jovyan

RUN mkdir extensions
COPY extensions .
RUN cd extensions
RUN pip install .
RUN cd ..

RUN pwd

USER root
# Run mongo while generating data.
COPY data_generator.py .data_generator.py
RUN mongod --smallfiles --fork --logpath /dev/null && /opt/conda/bin/python .data_generator.py
# old way:
# RUN mkdir dump
# COPY dump dump
# RUN mongod --fork --logpath /dev/null && \ 
#     mongorestore dump && \
#     rm -rf dump

# Copy content
COPY matplotlibrc /opt/conda/lib/python3.4/site-packages/matplotlib/mpl-data/
RUN mkdir tutorial
COPY tutorial tutorial
RUN mv tutorial/Welcome* .
# RUN mkdir datasets
# COPY datasets datasets
RUN mkdir .data-cache
COPY .data-cache .data-cache
RUN git clone https://github.com/jupyter/notebook
RUN mv notebook/docs/source/examples/Notebook jupyter-tutorial
RUN rm -rf notebook

# Stay root so that we can start system processes in server extensions.
USER root
RUN rm -rf extensions setup.py
RUN apt-get install -yq supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
