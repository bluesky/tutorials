# Bluesky Tutorial

This is undergoing major renovations. Come back in a day or two!

## Building for JupyterHub Deployment

```
jupyter-repo2docker --user-name=jovyan --no-run --image-name nsls2/tutorial:$(git rev-parse --short=6 HEAD) .
```
