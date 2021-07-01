# Contributing to the Tutorials

## Set up a development environment

1. Install [Docker](https://docs.docker.com/get-docker/) on your system. (For
   Podman fans: It must be actual Docker, not Podman, because the Docker Python
   bindings are used and these do not yet interoperate with Podman.)

   To confirm that you have a working Docker installation, run:

   ```
   docker run hello-world
   ```

   A small Docker image may be downloaded, and then you should see a message
   that begins, "Hello from Docker!"

2. Clone this repository and `cd` into the repository root.

   ```
   git clone https://github.com/bluesky/tutorials
   cd tutorials
   ```

2. Create a software environment for running and saving changes to the
   tutorial. (This environment will not contain the requirements for the
   tutorial itself.)

   ```
   # Create a new environment with conda...
   conda create -n bluesky-tutorials python=3.8
   conda activate bluesky-tutorials
   # or with Python's built-in venv...
   python3 -V  # Confirm version is 3.7 or higher.
   python3 -m venv .venv/
   source .venv/bin/activate
   ```

   ```
   # Install Python packages and git hooks.
   pip install -r binder/requirements-dev.txt
   pre-commit install
   ```

   Notice that we do *not* have to install `binder/requirements.txt` or any
   other requirements for the tutorial itself. That will be done inside
   a Docker container automatically in the next step.

3. Build and start this tutorial container.

   ```
   jupyter-repo2docker --editable .
   ```

   This process will take about a minute, perhaps longer the first time you run it.
   Finally, it will start a Jupyter server. Look for lines like
   ```
   To access the notebook, open this file in a browser:
       file:///home/dallan/.local/share/jupyter/runtime/nbserver-1-open.html
   Or copy and paste one of this URL:
       http://127.0.0.1:39827/?token=...
   ```
   in the output. When you are done, you can use Ctrl+C to stop the Jupyter server, as usual.

4. Navigate your Internet browser to the URL displayed by `jupyter-repo2docker`'s output.

5. Be sure to read the next section about committing changes!

## Commit changes

You can edit notebooks, scripts, and other files in the repository from
within JupyterLab or using any editor. You can save changes from JupyterLab
in the normal way. (Explanation: Because of the `--editable` option we passed
to `jupyter-repo2docker`, the container has mounted the working directly and
thus changes will persist outside the container.)

**Before you commit changes to git** the *output* area of the notebooks must be
be cleared. This ensures that (1) the potentially-large output artifacts
(such as figures) do not bloat the repository and (2) users visiting the
tutorial will see a clean notebook, uncluttered by any previous code
execution.

To clear the output areas in JupyterLab, go to Edit > Clear All Outputs. Then
save the notebook. Now it is safe to commit.

If you forget to do this, an error message will protect you from accidentally
committing. It looks like this:

```
$ git add .
$ git commit -m "oops"
nbstripout...............................................................Failed
- hook id: nbstripout
- files were modified by this hook
```

When happened here? Your attempt to commit has been blocked. The files have
been fixed for you---clearing the outputs from your notebooks. Before trying
again to commit, you must add those fixes to the "staged" changes.

```
# Stage again to include the fixes that we just applied (the cleared output areas).
$ git add .

# Now try committing again.
$ git commit -m "this will work"
nbstripout...............................................................Passed
[main 315536e] changed things
 2 files changed, 44 insertions(+), 18 deletions(-)
```

For details on the tools involved in this process see
[nbstripout](https://github.com/kynan/nbstripout) and
[pre-commit](https://pre-commit.com/).

## Specify software requirements

Edit ``binder/requirements.txt`` to modify the software environment that
JupyterLab runs in. There are other configuration files available to support
for system (`apt`) and conda packages. See
https://repo2docker.readthedocs.io/en/stable/configuration/index.html.

After making changes to the configuration, you will need to stop the
Jupyter server (Ctrl+C twice, as usual) and start it again. As before:

```
jupyter-repo2docker --editable .
```
