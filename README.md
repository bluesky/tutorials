# NSLS-II tmpnb instance

This is an instance of [tmpnb](http://github.com/jupyter/tmpnb), a public
deployment of Jupyter notebooks for unauthenticated access by the public. All
user-created content is ephemeral: it is scoped to a container that is
automatically destroyed after a period of inactivity (or after some maximum
period of usage, whichever happens first).

## Deployment

It is served behind nginx using a configuration based on the one used by Project
Jupyter to deploy their try.jupyter.org service.

```bash
service nginx start
```


Use ``make`` to build the docker and start a pool of
instances ready to receive users. You can adjust the pool size, timeout, and
other parameters in the Makefile.

```bash
git clone https://github.com/NSLS-II/tutorial-docker
cd tutorial-docker
make proxy
make tmpnb
```
