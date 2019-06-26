[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/bluesky/tutorial/master?urlpath=lab)

# Bluesky Tutorial

This is a collection of tutorials on data acquisition and analysis with bluesky.
It can be used in an Internet browser with no software installation.

[**Start here**](https://mybinder.org/v2/gh/bluesky/tutorial/master?urlpath=lab).

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

### Making Changes

* Install [supervisor](http://supervisord.org) using system package manager---
apt, Homebrew, etc. It is pip-installable but currently not in Python 3, so it
cannot be installed in the same environment with ``requirements.txt`` below.

* Install the Python requirements.

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
  binder/start jupyter lab
  ```

### Publishing Updates

#### Binder deployment

The Binder deployment will update automatically the first time someone requests
a session.

#### BNL JupyterHub deployment on AWS

The BNL JupyterHub deployment will automatically pull fresh copies of the
*content* but if the software requirements change, the Docker image must be
manually updated.

To build an publish an updated version of the Docker image:

```
jupyter-repo2docker --user-name=jovyan --no-run --image-name nsls2/tutorial:$(git rev-parse --short=6 HEAD) .
docker push $(git rev-parse --short=6 HEAD)
```

Using the first six characters of the current commit hash as the Docker tag is
just a convention to help us stay organized. If re-building a new copy of the
same content but with updated dependencies (say, pulling in an updated version
of bluesky), add a ``.N`` counting number after the hash, starting at ``.1``.

Then in the CI host on AWS, update the tag in the JupyterHub helm configuration,
``config.yaml``, and redeploy:

```
helm list  # Find <DEPLOYMENT_NAME>.
helm upgrade <DEPLOYMENT_NAME> jupyterhub/jupyterhub --version=v0.6 -f config.yaml
```
