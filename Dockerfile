FROM jupyter/minimal-notebook
MAINTAINER NSLS-II <https://nsls-ii.github.io>
USER $NB_USER

ENV ENV_NAME tutorial

COPY environment.yml .
RUN conda env create -n $ENV_NAME -f environment.yml && conda clean -yt
RUN rm environment.yml

COPY matplotlibrc $CONDA_DIR/envs/$ENV_NAME/lib/python3.4/site-packages/matplotlib/mpl-data/

COPY tutorial/* ./
RUN git clone https://github.com/jupyter/notebook
RUN mv notebook/docs/source/examples/Notebook jupyter-notebook-tutorial
RUN rm -rf notebook

RUN mkdir ~/.data-cache
RUN mkdir ~/scripts
COPY generate_sample_data.py scripts/
COPY make_broker.py scripts/

# Add shortcuts to distinguish pip for python2 and python3 envs
RUN ln -s $CONDA_DIR/envs/python2/bin/pip $CONDA_DIR/bin/pip2 && \
    ln -s $CONDA_DIR/bin/pip $CONDA_DIR/bin/pip3

USER root

# Install Python 2 kernel spec globally to avoid permission problems when
# NB_UID
# switching at runtime.
RUN $CONDA_DIR/envs/$ENV_NAME/bin/python -m ipykernel install

USER $NB_USER
