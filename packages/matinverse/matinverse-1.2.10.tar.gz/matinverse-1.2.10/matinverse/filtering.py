from jax import numpy as jnp
import jax
from matinverse import Geometry2D,Geometry3D
from typing import Callable
import matplotlib.pyplot as plt

def ConicFilter(geometry:            Geometry2D | Geometry3D,
                R:                   float,
                normalize_at_border: bool = True,
                FFT:                 bool = True
                )->Callable:
    """ Conic Filter 
    :param geometry: Geometry2D or Geometry3D object
    :param R: Filter radius in physical units
    :param normalize_at_border: If True, the filter is normalized at the border of the domain:
    Liu, Guilin, et al. "Image inpainting for irregular holes using partial convolutions." Proceedings of the European conference on computer vision (ECCV). 2018.
    :param FFT: If True, the convolution is performed using FFT. Otherwise, a direct convolution is used.
    :return: The convolution function
    """
    

    def f(p):
     
     tmp = jnp.linalg.norm(p - geometry.center)/R

     return jnp.where(tmp < 1, 1 - tmp, 0)
    
    kernel   = geometry.compute_function_on_centroids(f)


    convolve = geometry.convolve_with_kernel(kernel,FFT=FFT)    

    # Precompute the scaling factor
    if normalize_at_border:
        normalization  = convolve(geometry.mask)
        scale = jnp.where( normalization > 0, 1 /  normalization, 0)
    else:
     scale = 1/kernel.sum()


   
    @jax.jit
    def convolution(x):
       
        # Perform convolution on the masked input
        output = convolve(x*geometry.mask)

        return jnp.where(geometry.mask, output*scale, x)
    

    return convolution








