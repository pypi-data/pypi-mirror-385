import numpy as np
import nlopt
import jax
from typing import Callable, List
import jax.numpy as jnp
from jax.flatten_util import ravel_pytree
import math
import jax.tree_util as jtu
from typing import Any


class CCSAQ_Optimizer:

    def __init__(self,objective : Callable,
                      lower_bounds: dict,
                      upper_bounds: dict,
                      verbose:str=True
                 ):
    
            self.upper_bounds,self.unflatten = ravel_pytree(upper_bounds)
            self.lower_bounds = ravel_pytree(lower_bounds)[0]
            self.nDOFs = len(self.lower_bounds)
            self._set_objective_function(objective)
            self.constraints = []
            self.verbose = verbose
  
    def _set_objective_function(self,func):

       self.objective = jax.jit(jax.value_and_grad(func,has_aux=True))

    def add_inequality_constraint(self,func: Callable):

        def func_wrapper(x,*params):
                output, (to_print, aux) = func(x,*params)
                return output, (output, (to_print, aux))

        self.constraints.append(jax.jit(jax.jacrev(func_wrapper, has_aux=True)))

    def pretty_print(self,to_print):
              
         #--------------------
         for key, value in to_print.items():
             
                    print(key + ': ',end='')
                    if jnp.isscalar(value): value = [value]
                
                    for v in np.array(value).flatten():
                     print(f"{v:12.3E}", end='')
                     print(' ',end='')

        

    def _get_inequality_constraint_per_params(self,k,params,last):


        def constraint(results, x, grad):
            
            x_tree = self.unflatten(x)

            jac, (output, (to_print, aux)) = self.constraints[k](x_tree,*params)

            #Set results
            output = ravel_pytree(output)[0]
            results[...] = np.array(output,dtype=np.float64)

            if self.verbose:
             self.pretty_print(to_print)
             if last:
               print() 

            #Sert Jacobian
            x_leaves, x_treedef = jtu.tree_flatten(x_tree)
            jac_leaves, jac_treedef = jtu.tree_flatten(jac)
        
            # Process each leaf (parameter) and its corresponding jacobian
            jac_cols = []
            for i, (param_leaf, jac_leaf) in enumerate(zip(x_leaves, jac_leaves)):
             # Flatten the jacobian for this parameter leaf
             param_jac_flat = jac_leaf.reshape((len(output), -1))
             jac_cols.append(param_jac_flat)
        
            # Concatenate along parameter dimension (axis=1)
            grad_output = jnp.concatenate(jac_cols, axis=1)

            #Reshape to a m,n array
            grad[:] = np.array(grad_output ,dtype=np.float64)

            self.state['constraints'][k].append(results.copy())

            return None
        
        return constraint

        

    def _get_objective_function_per_params(self,params,last):
         
         def objective_fn(x,grad):

              (output,(to_print,aux)),grad_output = self.objective(self.unflatten(x),*params)

              self.iter +=1
              if self.verbose:
               print(f"Iter: {self.iter:4d} ",end='')
               self.pretty_print(to_print)
               if last:
                print()     
              #--------------------  

              self.state['aux'].append(aux)

              grad_output = ravel_pytree(grad_output)[0]

              grad[:] = np.array(grad_output,dtype=np.float64) 

              self.state['objective_function'].append(float(output))

              return float(output)   
         
         return objective_fn

    def minimize(self,
                 x0: Any,
                 params: tuple = (),
                 params_constraints: List[dict] = [],
                 maxeval:  int = 400,
                 constraint_tol: float = 1e-8,
                 ftol_rel: float = None,
                 ftol_abs: float = None,
                 stop_val: float = None,
                ):

            #Init state   
            self.iter = 0
            self.state = {'aux':[],'objective_function':[],'constraints':[[] for _ in range(len(self.constraints))]}

            opt = nlopt.opt(nlopt.LD_CCSAQ,self.nDOFs)

            Nc = sum([0 if p  is None else 1 for p in params_constraints])

            opt.set_min_objective(self._get_objective_function_per_params(params,Nc==0))

            #Add inequality constraints            
         
            for k in range(len(self.constraints)):
               
               if not params_constraints[k] is None:               

                leaves, _ = jax.tree_util.tree_flatten(jax.eval_shape(self.constraints[k],x0,*params_constraints[k])[1][0])
                
                N_constraints = sum(int(math.prod(leaf.shape)) for leaf in leaves)

                opt.add_inequality_mconstraint(self._get_inequality_constraint_per_params(k,params_constraints[k],k==Nc-1),N_constraints*[constraint_tol])


            opt.set_lower_bounds(self.lower_bounds)

            opt.set_upper_bounds(self.upper_bounds)

            #Exit criteria
            opt.set_maxeval(int(maxeval))

            if ftol_rel is not None:
               opt.set_ftol_rel(float(ftol_rel))

            if ftol_abs is not None:
               opt.set_ftol_abs(float(ftol_abs))

            if stop_val is not None:
               opt.set_stopval(float(stop_val))

            x = opt.optimize(ravel_pytree(x0)[0])   

            return self.unflatten(jnp.array(x)),opt.last_optimum_value()
    #---------------------------------
