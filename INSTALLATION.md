# Local Installation

## Alternatives

These tutorials can be run:

* In a web browser using a cloud-based service. This the easiest way to get
  started because you do not need to install anything. Visit
  https://mybinder.org/v2/gh/bluesky/tutorials/main.
* Using Docker, run as `docker run -p 8888:8888 nsls2/tutorials:latest`.

However, if you prefer a direct local installation, instructions follow.

## Instructions

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

* Start Jupyter.

  ```sh
  jupyter lab
  ```
