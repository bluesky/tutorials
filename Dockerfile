# Copyright (c) Jupyter Development Team.
FROM jupyter/minimal-notebook

MAINTAINER NSLS-II <https://nsls-ii.github.io>

USER root

# Install and start mongo
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
RUN echo "deb http://repo.mongodb.org/apt/debian wheezy/mongodb-org/3.0 main" | tee /etc/apt/sources.list.d/mongodb-org-3.0.list
RUN apt-get update
RUN apt-get install -y mongodb-org
RUN mkdir -p /data/db

USER jovyan

# Install Python 3 packages
RUN conda install --yes \
    'python=3.4*' \
    'ipywidgets=4.0*' \
    'pandas=0.16*' \
    'matplotlib=1.4*' \
    'scipy=0.15*' \
    'seaborn=0.6*' \
    'scikit-learn=0.16*' \
    'scikit-image=0.11*' \
    'sympy=0.7*' \
    'cython=0.22*' \
    'patsy=0.3*' \
    'statsmodels=0.6*' \
    'cloudpickle=0.1*' \
    'dill=0.2*' \
    'numba=0.20*' \
    'bokeh=0.9*' \
    && conda clean -yt

RUN conda install -c lightsource2 --yes \
    'metadatastore' \
    'databroker' \
    && conda clean -yt

# pip install things not yet on lightsource2 channel.
RUN conda install --yes pip
RUN pip install https://github.com/Nikea/history/zipball/master#egg=history
RUN pip install https://github.com/NSLS-II/bluesky/zipball/master#egg=bluesky
RUN pip install https://github.com/soft-matter/pims/zipball/master#egg=pims

# Configure MDS and FS connection parameters.
ENV MDS_HOST 127.0.0.1
ENV MDS_DATABASE demo-mds
ENV MDS_TIMEZONE US/Eastern
ENV MDS_PORT 27017
ENV FS_HOST 127.0.0.1
ENV FS_DATABASE demo-fs
ENV FS_PORT 27017

# Install Jupyter server extensions.
RUN mkdir extensions
COPY extensions .
RUN cd extensions
RUN pip install .
RUN cd ..

RUN pwd

USER root
# Run mongo while generating data.
COPY data_generator.py data_generator.py
RUN mongod --smallfiles --fork --logpath /dev/null && /opt/conda/bin/python data_generator.py
# old way:
# RUN mkdir dump
# COPY dump dump
# RUN mongod --fork --logpath /dev/null && \ 
#     mongorestore dump && \
#     rm -rf dump

# Copy content
RUN mkdir notebooks
COPY notebooks notebooks
RUN mv notebooks/Welcome* .
RUN mkdir datasets
COPY datasets datasets
RUN mkdir .data-cache
COPY .data-cache .data-cache

# Stay root so that we can start system processes in server extensions.
USER root
RUN rm -rf extensions setup.py
