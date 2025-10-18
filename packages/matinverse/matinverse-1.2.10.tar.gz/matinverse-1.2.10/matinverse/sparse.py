"""
NOTE: Adapted from: https://github.com/arpastrana/jax_fdm/blob/main/src/jax_fdm/equilibrium/sparse.py
       Waiting for the CPU backend to be added in https://jax.readthedocs.io/en/latest/_autosummary/jax.experimental.sparse.linalg.spsolve.html#jax.experimental.sparse.linalg.spsolve
NOTE: Sparse solver does not support forward mode auto-differentiation yet.
"""
import jax
import jax.numpy as jnp

from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve as spsolve_scipy
from functools import partial
import numpy as np
np.set_printoptions(precision=3, suppress=True) 

# ==========================================================================
# Sparse linear solver on CPU
# ==========================================================================

def _spsolve(data,rows,cols, b, stabilize=False):

    """
    A wrapper around scipy sparse linear solver that acts as a JAX pure callback.
    """
    def callback(data, rows, cols, _b, stabilize):

       
        if stabilize:
         ind = 0
         mask = (rows != ind) & (cols != ind)
         rows_masked, cols_masked = rows[mask], cols[mask]

         if data.ndim == 1:  # shape (N,)
            data_masked = data[mask]
            data_app = jnp.array([1.0])
         elif data.ndim == 2:  # shape (B, N)
            data_masked = data[:, mask]
            data_app = jnp.ones((data.shape[0], 1))
         else:
            raise ValueError(f"Unsupported data shape {data.shape}")

         data = jnp.concatenate([data_masked, data_app], axis=-1)
         rows = jnp.concatenate([rows_masked, jnp.array([ind])])
         cols = jnp.concatenate([cols_masked, jnp.array([ind])])

        
         _b = _b.at[ind].set(0.0)


        _A = csc_matrix((data, (rows, cols)),shape=(_b.shape[0], _b.shape[0]))

        
        N = b.shape[0] 
        
        
        x = spsolve_scipy(_A, _b).T


        if x.ndim == 1:
            x = x[None, :]  # Make it 2D for batching

        
        return x

    
    xk = jax.pure_callback(callback,  # callback function
                           b,  # return type is b
                           data,  # callback function arguments from here on
                           rows,
                           cols,
                           b.T,
                           stabilize,
                           vmap_method="sequential"
                           )

    return xk




# ==========================================================================
# Define sparse linear solver
# ==========================================================================
@jax.custom_vjp
def sparse_solve(data,rows,cols, b,stabilize=False):
    """
    The sparse linear solver.
    """

    if b.ndim == 1:
        b = b[None, :]  # Make it 2D for batching
 

    return _spsolve(data,rows,cols, b,stabilize=stabilize)

      

# ==========================================================================
# Forward and backward passes
# ==========================================================================

def sparse_solve_fwd(data,rows,cols, b,stabilize):
    """
    Forward pass of the sparse linear solver.

    Call the linear solve and save parameters and solution for the backward pass.
    """

    xk = sparse_solve(data,rows,cols,b,stabilize=stabilize)

    return xk,(xk,data,rows,cols,b,stabilize)


def sparse_solve_bwd(res, g):
    """
    Backward pass of the sparse linear solver.
    """

    xk,data,rows,cols,b,stabilize = res


    lam = sparse_solve(data,cols,rows,g,stabilize=stabilize)

    # the implicit constraint function for implicit differentiation
    def residual_fn(params):
        data, b = params
 
        return b - jnp.zeros_like(xk).at[:,rows].add(jnp.einsum('i,bi->bi',data,xk[:,cols]))

    params = (data, b)

    # Call vjp of residual_fn to compute gradient wrt params
    params_bar = jax.vjp(residual_fn, params)[1](lam)[0]

    return (params_bar[0],None,None,params_bar[1],None) 


sparse_solve.defvjp(sparse_solve_fwd, sparse_solve_bwd)



