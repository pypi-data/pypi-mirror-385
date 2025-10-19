"""


Node Boolean Math Items
^^^^^^^^^^^^^^^^^^^^^^^

:AND:             
  And.

  True when both inputs are true.

:OR:              
  Or.

  True when at least one input is true.

:NOT:             
  Not.

  Opposite of the input.

.. _rna-enum-node-boolean-math-items:

======================================================================

:NAND:            
  Not And.

  True when at least one input is false.

:NOR:             
  Nor.

  True when both inputs are false.

:XNOR:            
  Equal.

  True when both inputs are equal (exclusive nor).

:XOR:             
  Not Equal.

  True when both inputs are different (exclusive or).

======================================================================

:IMPLY:           
  Imply.

  True unless the first input is true and the second is false.

:NIMPLY:          
  Subtract.

  True when the first input is true and the second is false (not imply).

"""

import typing
