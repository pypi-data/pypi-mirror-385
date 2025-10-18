from .geometry2D import Geometry2D
from .geometry3D import Geometry3D
from .boundary_conditions import BoundaryConditions
from .fourier import Fourier
from .filtering import ConicFilter
from .visualizer import plot2D, movie2D

__all__ = [
    "Geometry2D",
    "Geometry3D",
    "BoundaryConditions",
    "Fourier",
    "ConicFilter",
    "plot2D",
    "movie2D",
]



#Suppress GPU warning
import logging
logging.getLogger("jax._src.xla_bridge").setLevel(logging.ERROR)

import jax

jax.config.update("jax_enable_x64",True)
jax.config.update("jax_log_compiles",0)


__version__ = "1.2.10"
