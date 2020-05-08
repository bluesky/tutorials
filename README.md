[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/bluesky/tutorials/master?urlpath=lab)

# Bluesky Tutorial

This is a collection of tutorials on data acquisition and analysis with bluesky.
It can be used in an Internet browser with no software installation.

[**Start here**](https://mybinder.org/v2/gh/bluesky/tutorials/master?urlpath=lab).

**We recommend using Google Chrome for best results, but any modern browser
is supported.**

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

## Contributing to this Tutorial

### Local Installation

* Install the requirements.

  ```
  pip install -r binder/requirements.txt
  pip install -r docs/requirements.txt
  pip install bluesky-tutorial-utils
  ```

* Install the JupyterLab extensions and re-build JupyterLab.

  ```
  jupyter labextension install @jupyter-widgets/jupyterlab-manager
  jupyter labextension install jupyter-matplotlib
  ```

* Start the IOCs.

  supervisord -c supervisor/supervisord.conf

  You can check their status at any time using

  ```sh
  supervisorctl -c supervisor/supervisord.conf status
  ```

* Start Jupyter.

  ```sh
  jupyter lab
  ```

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
longer than ``nbsphinx_timeout`` (configured to 60 seconds in
``docs/source/conf.py``) to execute. Special cases can be allowed by editing
cell or notebook metadata. These should be used sparingly.

* **Allow a cell to raise an exception.** Add the cell tag ``raises-exception``.
* **Hide a cell from the static view.** This is appropriate for cells that
  (only) display an interactive matplotlib canvas. Add the cell metadata:

  ```json
  {
    "nbsphinx": "hidden"
  }
  ```

  The cell will be executed, but the neither input nor output will be shown.
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
