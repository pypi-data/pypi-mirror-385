"""


Beztriple Interpolation Mode Items
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _rna-enum-beztriple-interpolation-mode-items:

**Interpolation**

Standard transitions between keyframes.

:CONSTANT:        
  Constant.

  No interpolation, value of A gets held until B is encountered.

:LINEAR:          
  Linear.

  Straight-line interpolation between A and B (i.e. no ease in/out).

:BEZIER:          
  Bézier.

  Smooth interpolation between A and B, with some control over curve shape.

**Easing (by strength)**

Predefined inertial transitions, useful for motion graphics (from least to most "dramatic").

:SINE:            
  Sinusoidal.

  Sinusoidal easing (weakest, almost linear but with a slight curvature).

:QUAD:            
  Quadratic.

  Quadratic easing.

:CUBIC:           
  Cubic.

  Cubic easing.

:QUART:           
  Quartic.

  Quartic easing.

:QUINT:           
  Quintic.

  Quintic easing.

:EXPO:            
  Exponential.

  Exponential easing (dramatic).

:CIRC:            
  Circular.

  Circular easing (strongest and most dynamic).

**Dynamic Effects**

Simple physics-inspired easing effects.

:BACK:            
  Back.

  Cubic easing with overshoot and settle.

:BOUNCE:          
  Bounce.

  Exponentially decaying parabolic bounce, like when objects collide.

:ELASTIC:         
  Elastic.

  Exponentially decaying sine wave, like an elastic band.

"""

import typing
