[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/NSLS-II/tutorial/master)

# Bluesky Tutorial

This is a collection of tutorials on data acquisition and analysis with bluesky.
It can be used in an Internet browser with no software installation. Click one
the links below to jump in.

This is free and open to the public. If you are prompted for a username and
password, use any username and leave the password blank.

**We recommend using Google Chrome for best results, but any modern browser
is supported.**

* [BNL deployment](http://a80ccdb475acc11e88b00021c84f1ed3-649460689.us-east-1.elb.amazonaws.com/)
* Backup: [Binder deployment](https://mybinder.org/v2/gh/NSLS-II/tutorial/master)

## Survey
Took our tutorial? Let us know how you thought of it so we can better improve
it!
[Survey](https://goo.gl/forms/WAWhkAIvEGVzIUdf2)

## References

* [NSLS-II Software Documentation Landing Page](https://nsls-ii.github.io)
* [Bluesky Documentation](https://nsls-ii.github.io/bluesky)
* [Ophyd Documentation](https://nsls-ii.github.io/ophyd)
* [Databroker Documentation](https://nsls-ii.github.io/databroker)
* [Our Gitter Chat Channel](https://gitter.im/NSLS-II/DAMA) (come here for questions)




## Contributing to this Tutorial

### Making Changes

Install the software requirements.

```
pip install -r requirements.txt
```

Additionally, install ``nbstripout``.

```
pip install nbstripout
```

This git repository is configured to use nbstripout to automatically scrub the
outputs from the notebooks when they are committed so that users see a clean
notebook with no stale outputs. This also keeps the repository smaller and the
versioning cleaner. Do not be surprised when some git commands are sluggish, as
output-scrubbing is being performed automatically in the background.

Set EPICS-related environment variables, necessary for some examples involving
pyepics or caproto.

```
source .env
```

Start Jupyter and edit away!

```
jupyter notebook
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

#### Old BNL deployment

This deployment uses tmpnb, which has been deprecated by Jupyter and will likely
soon to be taken offline.
