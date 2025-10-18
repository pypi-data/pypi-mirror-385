from jax import numpy as jnp
import jax
from typing import Callable,List
from matinverse.filtering import ConicFilter
from matinverse import Geometry2D,Geometry3D
from matinverse.projection import projection



def volume_fraction(minp,maxp):
     
      @jax.jit
      def func(x):

       V = jnp.sum(x)
       N  = len(x)
       p  = V/N

       values = []

       values.append(minp/p-1)
       values.append(1-maxp/p)

       return jnp.array(values),({'Volume':[p]},None)

      return func

    

def get_conic_radius_from_eta_e(L,eta_e):

 if (eta_e >= 0.5) and (eta_e < 0.75):
        return L / (2 * jnp.sqrt(eta_e - 0.5))
 elif (eta_e >= 0.75) and (eta_e <= 1):
        return L / (2 - 2 * jnp.sqrt(1 - eta_e))
 else:
        raise ValueError(
            "The erosion threshold point (eta_e) must be between 0.5 and 1."
        )
 

def lengthscale(geo:Geometry2D | Geometry3D,
                Ls  :float,
                SSP2:bool =False,
                normalize_at_border:bool=True)-> tuple[Callable,Callable]:
      """
      param: Ls is the lenghscale in physical units
      """
     
      #We follow this approach:
      #https://opg.optica.org/oe/fulltext.cfm?uri=oe-29-15-23916&id=453270
      #https://github.com/NanoComp/meep/blob/master/python/adjoint/filters.py
      #Zhou, M., Lazarov, B. S., Wang, F., & Sigmund, O. (2015). Minimum length scale in topology optimization by
      #geometric constraints. Computer Methods in Applied Mechanics and Engineering, 293, 266-282.

      eta_e = 0.75
      eta_d = 1-eta_e

      c0    = 64 * Ls**2

      R = get_conic_radius_from_eta_e(Ls,eta_e)

      filtering = ConicFilter(geo,R,normalize_at_border=normalize_at_border)

      #filtering = geo.convolve_with_kernel()

      smoothed_projection = projection(geo,SSP2=SSP2)
    
      @jax.jit
      def func(x:       jax.Array,
               beta:    float,
               epsilon: float = 1e-8):
        
        filtered_field  = filtering(x)

        grad_norm_square =  jnp.linalg.norm(geo.grad_interpolation(filtered_field),axis=-1)**2 #[1/m^2]
       
        common = jnp.exp(-c0*grad_norm_square)

        projected_field = smoothed_projection(filtered_field,beta=beta)        
       
        #solid
        Is  = projected_field*common
        Ls  = jnp.mean(Is*jnp.minimum(filtered_field - eta_e, 0)**2)

        #void
        Iv  = (1-projected_field)*common
        Lv  = jnp.mean(Iv*jnp.minimum(eta_d - filtered_field, 0)**2)

        constraint = jnp.array([Ls,Lv])/epsilon-1

        return constraint,({'Ls':constraint},{})
      
      @jax.jit
      def transform(x,beta):

          x = filtering(x)

          return smoothed_projection(x,beta=beta)        

      return func,transform

