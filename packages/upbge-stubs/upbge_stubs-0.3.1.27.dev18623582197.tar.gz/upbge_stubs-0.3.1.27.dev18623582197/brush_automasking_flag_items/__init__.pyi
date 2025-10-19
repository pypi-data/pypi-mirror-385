"""


Brush Automasking Flag Items
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:use_automasking_topology:
  Topology.

  Affect only vertices connected to the active vertex under the brush.

:use_automasking_face_sets:
  Face Sets.

  Affect only vertices that share Face Sets with the active vertex.

:use_automasking_boundary_edges:
  Mesh Boundary Auto-Masking.

  Do not affect non manifold boundary edges.

:use_automasking_boundary_face_sets:
  Face Sets Boundary Automasking.

  Do not affect vertices that belong to a Face Set boundary.

:use_automasking_cavity:
  Cavity Mask.

  Do not affect vertices on peaks, based on the surface curvature.

:use_automasking_cavity_inverted:
  Inverted Cavity Mask.

  Do not affect vertices within crevices, based on the surface curvature.

:use_automasking_custom_cavity_curve:
  Custom Cavity Curve.

  Use custom curve.

.. _rna-enum-brush-automasking-flag-items:

"""

import typing
