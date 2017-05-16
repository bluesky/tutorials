FROM jupyter/minimal-notebook
MAINTAINER NSLS-II <https://nsls-ii.github.io>
USER $NB_USER

ENV ENV_NAME tutorial
ENV PROFILE_NAME tutorial

RUN conda update conda
COPY environment.yml ./
RUN conda env create -n $ENV_NAME -f environment.yml && conda clean -yt
RUN rm environment.yml

COPY matplotlibrc $CONDA_DIR/envs/$ENV_NAME/lib/python3.5/site-packages/matplotlib/mpl-data/

# Copy NSLS-II tutorial notebooks.
COPY tutorial/ ./

# Copy upstream Jupyter's tutorials on using the notebook.
RUN mkdir jupyter-notebook-tutorial
COPY notebook/docs/source/examples/Notebook/* jupyter-notebook-tutorial/

# Copy scripts and create a hidden directory to hold sample data.
RUN mkdir /home/$NB_USER/.data-cache
RUN mkdir /home/$NB_USER/.amostra_files
RUN mkdir /home/$NB_USER/scripts
COPY scripts/* /home/$NB_USER/scripts/

# Add shortcuts to distinguish pip for python2 and python3 envs
RUN ln -s $CONDA_DIR/envs/python2/bin/pip $CONDA_DIR/bin/pip2 && \
    ln -s $CONDA_DIR/bin/pip $CONDA_DIR/bin/pip3

# Import matplotlib the first time to build the font cache.
ENV XDG_CACHE_HOME /home/$NB_USER/.cache/
RUN $CONDA_DIR/envs/$ENV_NAME/bin/python -c "import matplotlib.pyplot"

# Generate sample data.
RUN $CONDA_DIR/envs/$ENV_NAME/bin/python /home/$NB_USER/scripts/generate_sample_data.py

# Install kernel spec globally to avoid permission problems when NB_UID
# switching at runtime.
USER root
RUN $CONDA_DIR/envs/$ENV_NAME/bin/python -m ipykernel install
# Overwrite kernel.json with hand-rolled file that includes IPython profile.
COPY kernel.json /usr/local/share/jupyter/kernels/python3/kernel.json
USER $NB_USER

# Create an IPython profile and a file to startup.
RUN $CONDA_DIR/envs/$ENV_NAME/bin/ipython profile create $PROFILE_NAME
COPY startup/* /home/$NB_USER/.ipython/profile_$PROFILE_NAME/startup/

# Ensure $NB_USER has ownership of all files in home dir.
USER root
RUN chown -R $NB_USER /home/$NB_USER/
USER $NB_USER
ENV PATH $CONDA_DIR/envs/$ENV_NAME/bin:$PATH
