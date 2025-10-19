"""


Dt Method Loop Items
^^^^^^^^^^^^^^^^^^^^

:TOPOLOGY:        
  Topology.

  Copy from identical topology meshes.

:NEAREST_NORMAL:  
  Nearest Corner and Best Matching Normal.

  Copy from nearest corner which has the best matching normal.

:NEAREST_POLYNOR: 
  Nearest Corner and Best Matching Face Normal.

  Copy from nearest corner which has the face with the best matching normal to destination corner's face one.

:NEAREST_POLY:    
  Nearest Corner of Nearest Face.

  Copy from nearest corner of nearest face.

:POLYINTERP_NEAREST:
  Nearest Face Interpolated.

  Copy from interpolated corners of the nearest source face.

:POLYINTERP_LNORPROJ:
  Projected Face Interpolated.

  Copy from interpolated corners of the source face hit by corner normal projection.

.. _rna-enum-dt-method-loop-items:

"""

import typing
