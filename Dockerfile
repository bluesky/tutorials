FROM jupyter/minimal-notebook
MAINTAINER NSLS-II <https://nsls-ii.github.io>
USER $NB_USER

ENV ENV_NAME tutorial

COPY environment.yml .
RUN conda env create -n $ENV_NAME -f environment.yml && conda clean -yt
RUN rm environment.yml

COPY matplotlibrc $CONDA_DIR/envs/$ENV_NAME/lib/python3.4/site-packages/matplotlib/mpl-data/

# Copy NSLS-II tutorial notebooks.
COPY tutorial/* ./

# Copy upstream Jupyter's tutorials on using the notebook.
RUN mkdir jupyter-notebook-tutorial
COPY notebook/docs/source/examples/Notebook/* jupyter-notebook-tutorial/

# Copy scripts and create a hidden directory to hold sample data.
RUN mkdir ~/.data-cache
RUN mkdir ~/scripts
COPY generate_sample_data.py scripts/
COPY make_broker.py scripts/

# Add shortcuts to distinguish pip for python2 and python3 envs
RUN ln -s $CONDA_DIR/envs/python2/bin/pip $CONDA_DIR/bin/pip2 && \
    ln -s $CONDA_DIR/bin/pip $CONDA_DIR/bin/pip3

# Import matplotlib the first time to build the font cache.
ENV XDG_CACHE_HOME /home/$NB_USER/.cache/
RUN $CONDA_DIR/envs/$ENV_NAME/bin/python -c "import matplotlib.pyplot"

USER root

# Install kernel spec globally to avoid permission problems when NB_UID
# switching at runtime.
RUN $CONDA_DIR/envs/$ENV_NAME/bin/python -m ipykernel install

USER $NB_USER
