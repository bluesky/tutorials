#!/bin/bash

set -vxeuo pipefail

ENV_DIR=/tmp/bluesky-tutorial-env-`date -u +"%Y-%m-%dT%H%M%S"`
conda create --yes -p $ENV_DIR python=3
conda activate $ENV_DIR
python3 -m pip install -r binder/requirements.txt
./binder/postBuild
./binder/start jupyter lab
