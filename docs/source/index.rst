Bluesky Tutorials
=================

.. note::

   For the `NSLS-II Users Meeting 2020 Bluesky Workshop
   <https://nsls2cfnusersmeeting.bnl.gov/workshops/workshop.aspx?year=2020&id=163>`__
   we have set up `a gitter room
   <https://gitter.im/NSLS-II/users-meeting-2020>`__ for live support
   and discussion.

   Agenda:

   * :doc:`Access Saved Data`
   * :doc:`Slice and Interpolate Image Data`
   * :doc:`Higher Dimensional Data`
   * :doc:`Multi-dimensional Coordinates`
   * :doc:`X-ray Absorption Fine Structure/Monochromator Optimization`

These examples address a wide range of questions, such as:

* How do I configure bluesky to work with a new piece of hardware?
* How do I write a custom experiment "plan"?
* How do I visualize my data?

You can run these examples in a live sandbox in the cloud here: |Binder|

.. |Binder| image:: https://mybinder.org/badge.svg
   :target: https://mybinder.org/v2/gh/bluesky/tutorials/master?urlpath=lab

...or browse them non-interactively, following the links below.

Finally, experienced Python programmers who want to run the examples locally
may refer to the instructions at
https://github.com/bluesky/tutorials#bluesky-tutorials.

.. toctree::
   :maxdepth: 1
   :caption: Basic Usage

   Hello Python and Jupyter.ipynb
   Hello Bluesky.ipynb
   Access Saved Data.ipynb
   Let Us Do the Bookkeeping For You.ipynb

.. toctree::
   :maxdepth: 1
   :caption: For Controls Engineers

   Epics Signal.ipynb
   Flyer Basics.ipynb

.. toctree::
   :maxdepth: 1
   :caption: For Scientists

   Process Tabular Data with Pandas.ipynb
   Slice and Interpolate Image Data.ipynb
   Higher Dimensional Data.ipynb
   Multi-dimensional Coordinates.ipynb
   Export data to files with Suitcase.ipynb

.. toctree::
   :maxdepth: 2
   :caption: Applied Examples

   X-ray Absorption Fine Structure/index
