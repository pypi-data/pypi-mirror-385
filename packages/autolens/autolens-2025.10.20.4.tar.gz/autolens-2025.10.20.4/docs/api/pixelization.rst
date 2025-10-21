=============
Pixelizations
=============

Pixelization
------------

Groups all of the individual components used to reconstruct a galaxy via a
pixelization (an ``ImageMesh``, ``Mesh`` and ``Regularization``)

The ``Pixelization`` API documentation provides a comprehensive description of how pixelizaiton objects work and
their associated API.

**It is recommended you read this documentation before using pixelizations**.

.. currentmodule:: autolens

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :recursive:

   Pixelization

Image Mesh [ag.image_mesh]
--------------------------

.. currentmodule:: autoarray.inversion.pixelization.image_mesh

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :recursive:

   Overlay
   Hilbert
   KMeans

Mesh [ag.mesh]
--------------

.. currentmodule:: autoarray.inversion.pixelization.mesh

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :recursive:

   Rectangular
   Delaunay
   Voronoi
   Voronoi

Regularization [ag.reg]
-----------------------

.. currentmodule:: autoarray.inversion.regularization

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :recursive:

   Constant
   ConstantSplit
   AdaptiveBrightness
   AdaptiveBrightnessSplit

Settings
--------

.. currentmodule:: autolens

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :recursive:

   SettingsInversion

Mapper
------

.. currentmodule:: autolens

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :recursive:

   Mapper