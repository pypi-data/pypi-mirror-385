"""


Exr Codec Items
^^^^^^^^^^^^^^^

:NONE:            
  None.

  No compression.

:ZIP:             
  ZIP.

  Lossless zip compression of 16 row image blocks.

:PIZ:             
  PIZ.

  Lossless wavelet compression, effective for noisy/grainy images.

:DWAA:            
  DWAA (lossy).

  JPEG-like lossy compression on 32 row image blocks.

:DWAB:            
  DWAB (lossy).

  JPEG-like lossy compression on 256 row image blocks.

:ZIPS:            
  ZIPS.

  Lossless zip compression, each image row compressed separately.

:RLE:             
  RLE.

  Lossless run length encoding compression.

:PXR24:           
  Pxr24 (lossy).

  Lossy compression for 32 bit float images (stores 24 bits of each float).

:B44:             
  B44 (lossy).

  Lossy compression for 16 bit float images, at fixed 2.3:1 ratio.

:B44A:            
  B44A (lossy).

  Lossy compression for 16 bit float images, at fixed 2.3:1 ratio.

.. _rna-enum-exr-codec-items:

"""

import typing
