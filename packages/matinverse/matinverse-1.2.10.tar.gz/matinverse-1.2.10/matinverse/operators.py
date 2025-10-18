from .geometry2D import Geometry2D
from .geometry3D import Geometry3D
from .fields import Fields
import jax.numpy as jnp


def SurfaceIntegral(geometry: Geometry2D | Geometry3D, 
              data: jnp.ndarray, 
              condition,
              internal=False) -> jnp.ndarray:
         
         if internal:
           #This is when the face is not on the boundary, but it's internal (including periodic surfaces)
           inds = geometry.select_internal_boundary(condition)
           return jnp.einsum("...s,s -> ...", data[..., inds], geometry.areas[inds])

         inds = geometry.select_boundary(condition)
         return jnp.einsum("...s,s -> ...", data[..., inds], geometry.boundary_areas[inds])
    