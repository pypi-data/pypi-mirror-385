from jax import numpy as jnp
import jax
from functools import partial
import equinox as eqx
from matinverse.geometry3D import Geometry3D
from matinverse.geometry2D import Geometry2D
import matplotlib.pyplot as plt




@partial(jax.jit, static_argnames=['eta'])
def tanh_projection(x: jnp.array, 
                    beta: jnp.ndarray,
                    eta: float=0.5) -> jnp.array:

    def step(x):    
        return jnp.where(x > eta, 1.0, 0.)
    
 
    def general(x):
        
        return (jnp.tanh(beta * eta) + jnp.tanh(beta * (x - eta))) / (
            jnp.tanh(beta * eta) + jnp.tanh(beta * (1 - eta))
        )
    
    return jax.lax.cond(jnp.isinf(beta), step, general, x)




def projection(
    geo: Geometry3D | Geometry2D,
    eta: float = 0.5,
    SSP2: bool = False,
):
    #We assume uniform grid
    d = jnp.array(geo.size) / jnp.array(geo.grid)

    if d[0] != d[1]:
        raise NotImplementedError("Smoothed projection is implemented only for uniform grids.")

    R_smoothing = 0.55 * d[0]

    
    grad_norm_square = lambda x: jnp.sum(geo.grad_interpolation(x)**2,axis=-1)
 
    if SSP2:
        hessian_norm_square = lambda x: jnp.sum(geo.hessian_interpolation(x)**2, axis=(-2,-1))

    #@eqx.filter_jit
    def smoothed_projection(rho_filtered: jnp.array,
                            beta: jnp.ndarray):

        rho_projected = tanh_projection(rho_filtered, beta=beta, eta=eta)

    
        den_helper = grad_norm_square(rho_filtered)


        if SSP2:
            den_helper += hessian_norm_square(rho_filtered) * (R_smoothing)**2
              
        nonzero_norm = jnp.abs(den_helper) > 0

        den_norm = jnp.sqrt(jnp.where(nonzero_norm, den_helper, 1))

        den_eff = jnp.where(nonzero_norm, den_norm, 1)

        # The distance for the center of the pixel to the nearest interface
        d = (eta - rho_filtered)/ den_eff

        needs_smoothing = nonzero_norm & (jnp.abs(d) < R_smoothing)

        d_R = d / R_smoothing

        F_plus = jnp.where(
            needs_smoothing, 0.5 - 15 / 16 * d_R + 5 / 8 * d_R**3 - 3 / 16 * d_R**5, 1.0
           )
        # F(-d)
        F_minus = jnp.where(
            needs_smoothing, 0.5 + 15 / 16 * d_R - 5 / 8 * d_R**3 + 3 / 16 * d_R**5, 1.0
        )

        # Determine the upper and lower bounds of materials in the current pixel (before projection).
        rho_filtered_minus = rho_filtered - R_smoothing * den_eff * F_plus
        rho_filtered_plus  = rho_filtered + R_smoothing * den_eff * F_minus

        # Finally, we project the extents of our range.
        rho_minus_eff_projected = tanh_projection(rho_filtered_minus, beta=beta, eta=eta)
        rho_plus_eff_projected = tanh_projection(rho_filtered_plus, beta=beta, eta=eta)

        # Only apply smoothing to interfaces
        rho_projected_smoothed = (
            (1-F_plus)
        ) * rho_minus_eff_projected + F_plus * rho_plus_eff_projected

        return jnp.where(
            needs_smoothing,
            rho_projected_smoothed,
            rho_projected
        )
    
    
    return smoothed_projection
    
