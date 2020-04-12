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

* Install the requirements.

  ```
  pip install -r binder/requirements.txt
  ```

* Install the JupyterLab extensions and re-build JupyterLab.

  ```
  jupyter labextension install --no-build @jupyter-widgets/jupyterlab-manager
  jupyter labextension install --no-build jupyter-matplotlib
  jupyter lab build
  ```

* Start JupyterLab using the ``binder/start`` executable, which also ensures
  that supervisor is running and imports the tutorial's JupyterLab workspace.

  ```
  ./binder/start jupyter lab
  ```
