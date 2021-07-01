[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/bluesky/tutorials/master?urlpath=lab)

# Bluesky Tutorials

This is a collection of tutorials on data acquisition and analysis using Bluesky
and scientific Python generally. There are a couple ways to use it.

* Try it in the interactive sandbox in the cloud at
  https://mybinder.org/v2/gh/bluesky/tutorials/master?urlpath=lab.
* Browse the content non-interactively at https://blueskyproject.io/tutorials.
* Download this content and run it on your local machine. This is not
  recommended for novices. See further instructions below.

## Survey
Took our tutorial? Let us know how you thought of it so we can better improve
it!
[Survey](https://goo.gl/forms/WAWhkAIvEGVzIUdf2)

## References

* [Bluesky Software Documentation Landing Page](https://blueskyproject.io)
* [Bluesky Documentation](https://blueskyproject.io/bluesky)
* [Ophyd Documentation](https://blueskyproject.io/ophyd)
* [Databroker Documentation](https://blueskyproject.io/databroker)
* [Our Gitter Chat Channel](https://gitter.im/NSLS-II/DAMA) (come here for questions)
* [Python Help](https://www.oreilly.com/programming/free/files/python-for-scientists.pdf) : A collection of Python tutorials geared towards scientific data analysis.


### Local Installation

* We strongly recommend creating a fresh software environment. For example,
  using [conda](https://docs.conda.io/en/latest/miniconda.html):

  ```
  conda create -n bluesky-tutorials python=3.7
  conda activate bluesky-tutorials
  ```

* You will need ``git``. You can install that using ``conda``, for example, or
  from https://git-scm.com/downloads.

  ```
  conda install git
  ```

* You will also need ``nodejs``. You can install that using ``conda`` as well,
  or from  https://nodejs.org/en/download/.

  ```
  conda install -c conda-forge nodejs
  ```

* Ensure pip, setuptools, and numpy are up to date. This helps avoid some
  pitfalls in the steps to follow.

  ```
  python -m pip install --upgrade pip setuptools numpy
  ```

* Clone this repository.

  ```
  git clone https://github.com/bluesky/tutorials
  cd tutorials
  ```

* Install the requirements.

  ```
  python -m pip install -r binder/requirements.txt
  python -m pip install -e ./bluesky-tutorial-utils  # MUST use -e here
  ```

* Install the JupyterLab extensions.

  ```
  # Install extension that supports '%matplotlib widget'.
  jupyter labextension install @jupyter-widgets/jupyterlab-manager
  jupyter labextension install jupyter-matplotlib
  ```

* Start the simulated hardware. On Linux and OSX this can be done in one line
  using supervisor:

  ```sh
  supervisord -c supervisor/supervisord.conf
  ```

  You can check their status at any time using

  ```sh
  supervisorctl -c supervisor/supervisord.conf status
  ```

  On Windows it must be done manually:

  ```sh
  python3 -m caproto.ioc_examples.decay
  python3 -m caproto.ioc_examples.mini_beamline
  python3 -m caproto.ioc_examples.random_walk
  python3 -m caproto.ioc_examples.random_walk --prefix="random_walk:horiz-"
  python3 -m caproto.ioc_examples.random_walk --prefix="random_walk:vert-"
  python3 -m caproto.ioc_examples.simple
  python3 -m caproto.ioc_examples.thermo_sim
  python3 -m caproto.ioc_examples.trigger_with_pc
  ```

* Start Jupyter.

  ```sh
  jupyter lab
  ```

## Contributing to this tutorial

Install the docs requirements.

  ```
  python -m pip install -r docs/requirements.txt
  ```

We use [nbstripout](https://github.com/kynan/nbstripout) to ensure that the
cell outputs are not committed---only the inputs. (See below for why and how to
make exceptions to this.) It must be configured like so.

```
nbstripout --install
nbstripout --install --attributes .gitattributes
```

This command reverts both of the above:

```
nbstripout --uninstall
```

Be advised that this places an absolute path in a configuration file. If the
Python environment you are in is later removed or broken, you may need to repeat
installation.

### Building the documentation

This command copies (select) notebooks into ``docs/source/``, converts them
to ``.rst``, and builds static HTML documentation at ``docs/build/html/``.

  ```sh
  make -C docs html
  ```

### Controlling Execution

For testing the notebooks and publishing static renderings of them, we execute
them with [nbsphinx](https://nbsphinx.readthedocs.io/). It will execute each
notebook top to bottom and fail if any of the cells raise exceptions or take
longer than ``nbsphinx_timeout`` (configured to 600 seconds in
``docs/source/conf.py``) to execute. Special cases can be allowed by editing
cell or notebook metadata. These should be used sparingly.

* **Allow a cell to raise an exception.** Add the cell tag ``raises-exception``.
* **Manually execute a notebook.** Add the notebook metadata:

  ```json
  {
    "keep_output": true,
  }
  ```

  This setting affects [nbstripout](https://github.com/kynan/nbstripout).
  Normally, nbstripout will remove the outputs from every cell when a notebook is
  committed. This will leave all the cells' outputs intact. When nbsphinx runs it
  will skip execution and render the existing outputs. This is useful for
  notebooks that have a very long execution time, contain client-specific outputs,
  like the output from ``bluesky.plans.count?`` in JupyterLab, or require
  user-initiated interruption, like RunEngine pause/resume. While `nbstripout`
  supports applying this at the level of specific cells, it must be applied to
  the whole notebook to play well with nbsphinx.

For more see https://nbsphinx.readthedocs.io/en/0.7.0/executing-notebooks.html.
