from typing import Callable
from jax import numpy as jnp
from functools import partial
import jax
from matplotlib.pyplot import axis
from  matinverse.geometry2D import Geometry2D
from  matinverse.geometry3D import Geometry3D
from  matinverse.boundary_conditions import BoundaryConditions
from  matinverse.sparse import sparse_solve
from   matinverse.fields import Fields
import lineax as lx
from typing import Any
import optimistix as optx
import diffrax
import numpy as np
import math


def unravel_indices(shape):
    """Return all index tuples for a given shape (Fortran order)."""
    size = math.prod(shape)  # pure Python
    coords = []
    for axis, dim in enumerate(shape):
        stride = math.prod(shape[:axis]) if axis > 0 else 1
        coords.append((jnp.arange(size) // stride) % dim)
    return jnp.stack(coords, axis=1)

def Fourier( geo:                           Geometry2D | Geometry3D,\
             boundary_conditions:           BoundaryConditions,\
             thermal_conductivity:          Callable|None = None,\
             heat_capacity:                 Callable|None = None,\
             conductance:                   Callable|None = None,\
             heat_source:                   Callable|None = None,\
             compute_side_flux:             Callable|None = None,\
             mode:                          str           = 'linear',\
             linear_solver:                 str           = 'direct',\
             unique_axis:                   int|None      = None,\
             batch_map:                     tuple         = (1,),\
             tol:                           float         = 1e-9,\
             maxiter:                       int           = 5000,\
             maxiter_nonlinear:             int           = 100,\
             scale_nonlinear:               float         = None,\
             maxiter_transient:             int           = 10000,\
             saveat:                        np.ndarray|None = None,\
             DT:                            float         = 1.0,\
             NT:                            int           = 1,\
             X0:                            Any           = None
             )->Any:
        r"""Differentiable Fourier solver based on the Finite-volume method.

         :param geo: The geometry object containing the mesh information.

         :param boundary_conditions: The boundary conditions object

         :param thermal_conductivity: A function that takes batch, space (as a function of volume index), temperature and time and returns the thermal conductivity tensor :math:`[\mathrm{W\,m^{-1}\,K^{-1}}]`

            Example::

               thermal_conductivity = lambda batch, space, temp, t: 100.*jnp.eye(geo.dim)
         :param heat_capacity: A function that takes batch, space (as a function of volume index), temperature and time and returns the heat capacity :math:`[\mathrm{J\,m^{-3}\,K^{-1}}]`.
            Example::

               heat_capacity = lambda batch, space, temp, t: 1e3 

         :param conductance: A function that takes the indices of the volumes adjacent to a given side and returns the batched conductance :math:`[\mathrm{W\,m^{-2}\,K^{-1}}]`. If not provided, it is assumed to be large number so it won't affect calculation.      


            Example::
               conductance = lambda s1,s2: 1e3*jnp.ones(1) #assuming a single batch and uniform conductance

         :param heat_source: A function that takes batch, space (as a function of volume index) and time and returns the heat source :math:`[\mathrm{W\,m^{-3}}]`. If not provided, it is assumed to be zero.

            Example::
               heat_source = lambda b,s,t: 1e5 
         
         :param mode: The mode of the solver. Can be 'linear', 'nonlinear' or 'transient'.

         :param linear_solver: The linear solver to use. Can be 'iterative' or 'direct'. If 'iterative', it uses the GMRES method. If 'direct', it uses sparse LU factorization.

         :param collapse_direct: If ``True``, it uses the same assembly matrix for all the batches in the direct solver. It can be used only for direct solvers and if no Robin BCs are used.

         :param compute_side_flux: A jnp.array containing the indices of the sides for which the flux will be computed. If not provided, no internal interfacial flux will be computed.

         :param batch_size: The number of batches to use. If > 1, the solver will be vectorized over the batches.

         :param tol: The tolerance for the linear solver.

         :param maxiter: The maximum number of iterations for the solver.

         :param maxiter_nonlinear: The maximum number of iterations for the nonlinear solver (default is 100). It is used only if ``mode='nonlinear'``. 

         :param scale_nonlinear: A scaling factor for the nonlinear solver. If not provided, it is set to :math:`10^{-4} dx^2` It is used only if ``mode='nonlinear'``.

         :param maxiter_transient: The maximum number of iterations for the transient solver (default is 10000). It is used only if ``mode='transient'``.

         :param saveat: A jnp.array containing the time steps at which the solution will be saved. If not provided, it saves all time steps.

         :param DT: The time step for the transient solver.

         :param NT: The number of time steps for the transient solver.

         :param X0: The initial guess for the temperature. It is expected to be of shape ``(batch_size, geo.nDOFs)``. If ``batch_size = 1`` then it can be a 1D array. If not provided, it is assumed to be zero.

       
         :return: A tuple containing the output dictionary and the statistics dictionary. The output dictionary contains the following fields:

         - 'T': The temperature field of shape ``(NT, batch_size, geo.nDOFs)``. 
         - 'J': The heat flux field of shape ``(NT, batch_size, geo.nDOFs, geo.dim)``. 
         - 'kappa': The thermal conductivity tensor field of shape ``(NT, batch_size, geo.nDOFs, geo.dim, geo.dim)``.
         - 'kappa_effective': The effective thermal conductivity field of shape ``(NT, batch_size, geo.nDOFs)``.
         - 'P_boundary': The boundary flux field of shape ``(NT, batch_size, geo.nBoundarySides)``.
         - 'P_internal': The internal flux field of shape ``(NT, batch_size, geo.nSides)``.
         - 'T_boundary': The temperature field at the boundaries of shape ``(NT, batch_size, geo.nBoundarySides)``.
        
         The statistics dictionary contains the following fields:
         
          - 'num_steps': The number of steps taken by the nonlinear solver.

        """
        if saveat is None:
         saveat = np.arange(0, DT*NT, DT)

        NT_save = len(saveat)

        

        #Total number of batches
        #batch_size = int(np.prod(np.array(batch_map)))

        #Indices for the batches (support up to 2D batch maps)
        #ii, jj = np.indices(np.array(batch_map), dtype=int)
        #batch_indices = np.stack([ii.ravel(order="F"), jj.ravel(order="F")], axis=1)

       
        batch_indices = unravel_indices(batch_map)
        batch_size = math.prod(batch_map) 
        batch_1D = jnp.arange(batch_size)
        #---------------------------------------
        #In case we have only one axis to vmap over
        if batch_indices.shape[1] == 1:
          batch_indices = batch_indices[:,0]
      
       
         
        if X0 is None:
         X0 = jnp.zeros((batch_size, geo.nDOFs))

        if thermal_conductivity is None:
          thermal_conductivity = lambda batch, space, temp, t: jnp.eye(geo.dim)

        if heat_capacity is None:
           heat_capacity = lambda batch, space, temp, t: 1 

        if heat_source is None:
          heat_source =lambda b,s,t:0

        N          = geo.nDOFs

        #Compute indices for grid 
        
        #Prepare the output structure
        stats = {}


        if compute_side_flux is None:
           compute_side_flux = jnp.array([], dtype=jnp.int32)
        

        bcs = boundary_conditions
    
        if not scale_nonlinear:
         scale = 1e-4*(geo.size[0]/geo.grid[0])**2
        else:
          scale = scale_nonlinear 

        #This assumes that h_ij = h_ji
        if not conductance:
          conductance = lambda x,t:1e10*jnp.ones((batch_size,geo.smap.shape[0]))
        else:
          conductance = geo.cell2side(conductance) 

 
        #if not X0: X0    = jnp.zeros((batch_size,N))
        if X0.ndim == 1: X0 = jnp.tile(X0,(batch_size,1))

       
        rows       = jnp.hstack((geo.smap[:,0],geo.smap[:,1],np.arange(N)))
        cols       = jnp.hstack((geo.smap[:,1],geo.smap[:,0],np.arange(N)))  

        #Non linearity Create TB0 from X0 [assuming 0 flux]]------------------------------------
        
        flux_sides   = bcs.get_flux_sides()
        
        flux_elems   = geo.boundary_sides[flux_sides]
       
        N_flux_sides = len(flux_elems)
        TB0          = X0[:,flux_elems]
        rows         = jnp.hstack((rows,jnp.arange(N_flux_sides)+N,jnp.arange(N_flux_sides)+N))
        cols         = jnp.hstack((cols,jnp.arange(N_flux_sides)+N,flux_elems))  
        #rows         = jnp.hstack((rows,flux_elems,flux_elems,                jnp.arange(N_flux_sides)+N,jnp.arange(N_flux_sides)+N))
        #cols         = jnp.hstack((cols,flux_elems,jnp.arange(N_flux_sides)+N,flux_elems,                jnp.arange(N_flux_sides)+N))  
        T0 = jnp.concatenate([X0,TB0], axis=1) 

        #Tangential contribution
        #This is only off-diagonal
        #T_rows = jnp.concatenate((geo.smap[geo.T_indices[:,0],0],geo.smap[geo.T_indices[:,0],1]), axis=0)

        #T_rows=geo.smap[geo.T_indices[:,0]].flatten(order='F')

       
       

        #rows   = jnp.concatenate((rows,T_rows), axis=0)
        #T_cols = jnp.concatenate((geo.T_indices[:,1],geo.T_indices[:,1]), axis=0)
        #cols   = jnp.concatenate((cols,T_cols), axis=0)
        #---------------------------------------------
        # print(geo.face_centroids[6])
        # quit()
        # for s in geo.T_indices:
        #   if s[0] == 6:
        #     print(s[1])
        # quit()    

      

        #@jax.jit
        def Laplacian(X,t):
         
         T  = X[:,:N]
         Tb = X[:,N:]

         B          = jnp.zeros((batch_size,N+N_flux_sides))
        
         

         kappa = jax.vmap(
                lambda b: jax.vmap(
                    thermal_conductivity, 
                    in_axes=(None, 0, 0, None), 
                   out_axes=0
                  )(batch_indices[b],geo.cell_id, T[b], t)
         )(batch_1D)
      

         cond = partial(conductance,t=t)(T)
        
         kappa_i  =  jnp.einsum('si,...sij,sj->...s',geo.normals,kappa[:,geo.smap[:,0]],geo.normals)
         kappa_j  =  jnp.einsum('si,...sij,sj->...s',geo.normals,kappa[:,geo.smap[:,1]],geo.normals)

         #cf       = 2*jnp.einsum('...s,s->...s',kappa_i*kappa_j/cond,1/geo.dists)
         #kappa_ij = 2*kappa_i * kappa_j/(kappa_i + kappa_j + cf)

        
         #Normal
         kappa_ij = kappa_i * kappa_j/(kappa_i*geo.dists[None,1] + kappa_j*geo.dists[None,0]) #This is k/L, so it is a conductance.

         #Orthogonal
         denomimator = kappa_i*geo.dists[None,1]+kappa_j*geo.dists[None,0]
         numerator   = jnp.einsum('bs,bsij->bsij',kappa_i*geo.dists[None,1],kappa[:,geo.smap[:,1]]) + \
                       jnp.einsum('bs,bsij->bsij',kappa_j*geo.dists[None,0],kappa[:,geo.smap[:,0]])
         k_parallel  = jnp.einsum('bsij,bs,s->bsj',numerator,1/denomimator,geo.areas)

         #Normal flux---Off-diagonal terms
         bulk_d = jnp.einsum('...s,s->...s',kappa_ij,geo.areas)
         
         #Normal flux---Diagonal terms
         d = jnp.zeros((batch_size,N)).at[:,geo.smap[:,0]].add(bulk_d).\
                                       at[:,geo.smap[:,1]].add(bulk_d)
         
         
         #Thermalizing Boundaries        
         thermo_sides = bcs.get_temperature_sides()
         thermo_values = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_temperature_values(b,s,t))(jnp.arange(len(thermo_sides))))(batch_indices)
       
         side_normals  = jnp.array(geo.boundary_normals)[thermo_sides]
         thermo_elems  = jnp.array(geo.boundary_sides)[thermo_sides]

         kappa_b = jnp.einsum('si,...sij,sj->...s',side_normals,kappa[:,thermo_elems],side_normals)
         
         factor =  geo.boundary_areas[thermo_sides]/geo.boundary_dists[thermo_sides]
         d =  d.at[:,thermo_elems].add(jnp.einsum('...s,s->...s',kappa_b,factor))
         tmp = jnp.einsum('...s,...s->...s',thermo_values,kappa_b)
         B =  B.at[:,thermo_elems].add(jnp.einsum('...s,s->...s',tmp,factor))

         #Flux Boundaries 
         flux_sides  = bcs.get_flux_sides()
         flux_elems  = geo.boundary_sides[flux_sides]  
         kappa_b     = jnp.einsum('si,...sij,sj->...s',geo.boundary_normals[flux_sides],kappa[:,flux_elems],geo.boundary_normals[flux_sides])

         
         if len(flux_sides) > 0:
          #flux_values = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_flux_values(b,s,t,Tb[b,s]))(jnp.arange(len(flux_sides))))(jnp.arange(batch_size))
          #flux_values = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_flux_values(b,s,t,Tb[b,s]))(jnp.arange(len(flux_sides))))(batch_indices)
          flux_values = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_flux_values(batch_indices[b],s,t,Tb[b,s]))(jnp.arange(len(flux_sides))))(batch_1D)
          factor      = geo.boundary_areas[flux_sides]

          #B           = B.at[:,flux_elems].add(-jnp.einsum('...s,s->s',flux_values,factor))  
          B = B.at[:, flux_elems].add(-jnp.einsum('...s,s->...s', flux_values, factor))

          #Nonlinear component (flux sizes)
          B           = B.at[:,N:].add(-geo.boundary_dists[flux_sides][jnp.newaxis,:] * flux_values/kappa_b)

         
         #else:
         # flux_values = jnp.zeros((batch_size,len(flux_sides)))
         #B           = B.at[:,N:].add(-jnp.einsum('...s,s->s',flux_values,factor))
         #factor      = geo.boundary_areas[flux_sides]/geo.boundary_dists[flux_sides]/geo.V
         #tmp         = jnp.einsum('...s,s->...s',kappa_b,factor)
         #data_flux   = jnp.concatenate([-tmp,tmp,tmp,-tmp], axis=1)
         #print(data_flux.shape)
         #quit()


         #----------------------------
        
         #Robin boundary
         robin_sides     = bcs.get_robin_sides()
         #robin_h,robin_T = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_robin_values(b,s,t))(jnp.arange(len(robin_sides))))(jnp.arange(batch_size))
         robin_h,robin_T = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_robin_values(b,s,t))(jnp.arange(len(robin_sides))))(batch_indices)
         robin_elems     = geo.boundary_sides[robin_sides]
         side_normals    = geo.boundary_normals[robin_sides]
         
      
         kappa_b = jnp.einsum('si,...sij,sj->...s',side_normals,kappa[:,robin_elems],side_normals)
         gamma   = jnp.einsum('...s,s,...s->...s',robin_h,geo.boundary_dists[robin_sides],1/kappa_b)
         h_star = robin_h/(gamma+1)
         areas = geo.boundary_areas[robin_sides]
         common_factor = jnp.einsum('...s,s->...s',h_star,areas)
         B  = B.at[:,robin_elems].add(common_factor*robin_T)
         d  = d.at[:,robin_elems].add(common_factor)
         #---------------------------------------
         


         #Periodic 
         p_sides,p_values = (lambda t: jax.vmap(lambda b: bcs.get_periodic(b, t),0,(None,0))(batch_indices))(t)
       
         p_elems  = geo.smap[p_sides]
        
         #Normal contribution
         P        = jnp.zeros_like(B)
         tmp      = jnp.einsum('...s,...s->...s',bulk_d[:,p_sides],p_values) #off diagonal

         P        = P.at[:,p_elems[:,0]].add( tmp)
         P        = P.at[:,p_elems[:,1]].add(-tmp) 

        
         #Orthogonal contribution
         #tmp = jnp.einsum('bsj,sej,bs->bs',k_parallel[:,p_sides,:],geo.g_data_new[p_sides,1],p_values)
         #P        = P.at[:,p_elems[:,0]].add( tmp)
         #P        = P.at[:,p_elems[:,1]].add( tmp)  #we have double negation
         
         B       += P

       


        
         data   = jnp.hstack((-bulk_d,-bulk_d,d))

         #{reserves symmetry}        
         #data   = jnp.hstack((data,-data_flux))
         
         #Add nonlinear boundary conditions
        
         if N_flux_sides > 0:
          nonlinear_data = jnp.ones(N_flux_sides)
          repeated_data = jnp.tile(nonlinear_data[None, :], (batch_size, 1))         
          data = jnp.hstack((data,repeated_data,-repeated_data))
         #----------------------------------

         #Add tangential fluxes
    
         #T_data = jnp.einsum('bsj,sj->bs',k_parallel[:,geo.T_indices[:,0],:],geo.g_data)
         #data   = jnp.hstack((data,-T_data,T_data)) 


  
         return data,B

        
        #Solve
        if mode =='nonlinear':

         H = jax.vmap(lambda b: jax.vmap(lambda s:heat_source(b,s,0)*geo.self.V[s])(jnp.arange(N))) (batch_indices)

         H = jnp.concatenate([H, jnp.zeros((batch_size,N_flux_sides))], axis=1) 
         
         def fn(x,args):
           
           data,B = Laplacian(x,0) 


           L = jnp.zeros_like(x).at[:,rows].add(jnp.einsum('ks,ks->ks',data,x[:,cols]))

           RES = L - B - H
           
           return RES*scale

           #return L - B - H
           #return jnp.zeros_like(x).at[:,rows].add(jnp.einsum('ks,ks->ks',data,x[:,cols]))  - B

         #linaer_solver = lx.AutoLinearSolver(well_posed=False)
         #linear_solver = lx.BiCGStab(atol=1e-12,rtol=1e-12)
         #linear_solver = lx.GMRES(atol=1e-12,rtol=1e-12)
         linear_solver =lx.LU()#AutoLinearSolver(well_posed=False)

         solve  = optx.Newton(rtol=1e-12,atol=1e-12,linear_solver=linear_solver)
         
         #print(solve.linear_solver)
         #quit()

         
         X0 = jnp.concatenate([X0,TB0], axis=1) #Concatenate the initial guess with the boundary conditions``

         out    = optx.root_find(fn, solve, X0,max_steps=maxiter_nonlinear)

         stats.update(out.stats)

         #stats['num_steps'] = out.stats['num_steps']
         #print(out.stats['num_steps'])

         X = out.value

      
         T  = X[:,:N]
         TB = X[:,N:] 
        
        elif mode == 'linear':
          

         data,B = Laplacian(T0,0) 


         L = lambda x: jnp.zeros_like(x).at[:,rows].add(jnp.einsum('ks,ks->ks',data,x[:,cols]))

         #H = lambda t:jax.vmap(lambda b: jax.vmap(lambda s:heat_source(b,s,t)*geo.V[s])(jnp.arange(N))) (jnp.arange(batch_size))
         H = lambda t:jax.vmap(lambda b: jax.vmap(lambda s:heat_source(b,s,t)*geo.V[s])(jnp.arange(N))) (batch_indices)

         H = jax.vmap(H)(jnp.arange(NT_save))
        

         if N_flux_sides > 0:
          #This just pads H 
          H_concatenate = jnp.concatenate([H, jnp.zeros((NT_save,batch_size,N_flux_sides))], axis=2)
         else:
          H_concatenate = H

         if linear_solver == 'iterative':
          X,info = jax.scipy.sparse.linalg.cg(L,B+H_concatenate[0],tol=tol,x0=T0,maxiter=maxiter)

         elif linear_solver == 'direct':

          #Reduce the system if it is periodic everywhere

          B_tot = B+H_concatenate[0]
          if geo.boundary_sides.shape[0] == 0 :
            #The system is periodic everywhere so the matrix is singular. We'll fix a zero-temperature node.
            stabilize = True
          else:
            stabilize = False  
                   
          #Solve
          
          if unique_axis == 'all':
           
           B_slice = jnp.arange(batch_size)[None,:]
           A_slice = jnp.array([0])

          elif not unique_axis == None:
            groups = jnp.arange(batch_size).reshape(*batch_map,order='F')
            B_slice = jnp.moveaxis(groups,unique_axis, 0)
            A_slice = B_slice[:, 0].ravel()  
          else:
            groups = jnp.arange(batch_size)
            B_slice = groups[:,None] 
            A_slice = groups 
               
       
          X = jax.vmap(sparse_solve, in_axes=(0,None,None,0,None))(data[A_slice],rows,cols,B_tot[B_slice],stabilize).reshape(batch_size, -1,order='F')

          #X = jax.vmap(sparse_solve, in_axes=(0,None,None,0,None))(data,rows,cols,B_tot,stabilize)


      


          #Test
          # groups = jnp.arange(batch_size)
          # B_slice = groups
          # A_slice = groups 
          # X = jax.vmap(sparse_solve, in_axes=(0,None,None,0,None))(data[A_slice],rows,cols,B_tot[B_slice],stabilize).reshape(batch_size, -1,order='F')

          #print(jnp.allclose(X,X2))





          
         T = X[:,:N] #Get only the temperature values, not the boundary ones
         TB = X[:,N:]
         #operator = lx.FunctionLinearOperator(fn=L,tags=lx.positive_semidefinite_tag,input_structure=jax.eval_shape(lambda: jnp.zeros((batch_size,N))))
         #out = lx.linear_solve(operator, B + H,options={'y0':jax.lax.stop_gradient(X0)})  
         #T = out.value
         #T = jnp.ones_like(X0)
         
         
        elif mode == 'transient':
 
          #DT = kwargs['DT']

          #H = lambda t: jax.vmap(lambda b: jax.vmap(lambda s:heat_source(b,s,t)*geo.V[s])(jnp.arange(N))) (jnp.arange(batch_size))
          H = lambda t: jax.vmap(lambda b: jax.vmap(lambda s:heat_source(b,s,t)*geo.V[s])(jnp.arange(N))) (batch_indices)


          # #Add nonlinearity
         
          # def update(y, t):

          #   data,B = Laplacian(y[t-1],t)           
          #   L = jnp.zeros((batch_size,N+N_flux_sides)).at[:,rows].add(jnp.einsum('ks,ks->ks',data,y[:,:,cols][t-1]))
          #   LAPLACIAN = L[:,:N]
            
          
          #   #Heat capacity [batch,space]       
          #   C = jax.vmap(lambda b: jax.vmap(lambda s: heat_capacity(b,s,y[t,b,s],t))(jnp.arange(N)))(jnp.arange(batch_size))      
            
          #   T = y[t-1,:,:N] + DT/C*(B[:,:N] + H(t) - LAPLACIAN)

          #   TB = T[:,flux_elems] + L[:,N:]

          #   y_new = jnp.concatenate([T,TB], axis=1)

          #   y = y.at[t].set(y_new)
          #   return y,None

          # y_init = jnp.zeros((NT,batch_size,N+N_flux_sides)).at[0].set(T0)

          # X, _ = jax.lax.scan(update, y_init,jnp.arange(NT))

          # T  = X[:,:,:N] #Get only the temperature values, not the boundary ones
          # TB = X[:,:,N:]
        
          # #DIFFRAX
          def vector_field(t, y, args):
           
            y = jnp.concatenate([y,TB0], axis=1)

            data,B = Laplacian(y,t)   

              
            L = jnp.zeros((batch_size,N+N_flux_sides)).at[:,rows].add(jnp.einsum('ks,ks->ks',data,y[:,cols]))
            LAPLACIAN = L[:,:N]
            B_tot     = B[:,:N] + H(t)


            C = jax.vmap(lambda b: jax.vmap(lambda s: heat_capacity(batch_indices[b],s,y,t))(jnp.arange(N)))(batch_1D)       


            return (B_tot - LAPLACIAN)/C

            #TB =  EQ_RES[:,flux_elems]*0 #TO DO

            #return  jnp.concatenate([EQ_RES,TB], axis=1)[0]
          
          
          # Tolerances
          rtol = 1e-10
          atol = 1e-10
          stepsize_controller = diffrax.PIDController(
          pcoeff=0.3, icoeff=0.4, rtol=rtol, atol=atol, dtmax=0.001
          )
       
      
          #solver = CrankNicolson(rtol=rtol,atol=atol)
          solver = diffrax.Tsit5()

          term = diffrax.ODETerm(vector_field)

          #X0 = jnp.concatenate([X0,TB0], axis=1)
          out = diffrax.diffeqsolve(
               term,
               solver,
               0,
               DT*NT,
               DT,
               X0,
               saveat=diffrax.SaveAt(ts=saveat),
               stepsize_controller=stepsize_controller,
               max_steps=maxiter_transient
          )

          X = out.ys
          #print(out.stats)

          #T = X[:,:,:N] #Get only the temperature values, not the boundary ones
          #TB = X[:,:,N:]
          T = X
     
          TB = jnp.zeros((NT_save,batch_size,N_flux_sides)) #TO DO: Add the boundary conditions for the transient case
          
       
        #@jax.jit
        def get_flux(X,Tb,kappa,conductance,t):
        
        
         #Flux calculations (using Gauss)
         J                = jnp.zeros((batch_size,N,geo.dim))

         P_boundary       = jnp.zeros((batch_size,len(geo.boundary_sides)))       
         T_boundary = jnp.zeros((batch_size,geo.boundary_sides.shape[0]))

         kappa_i          =  jnp.einsum('si,...sij,sj->...s',geo.normals,kappa[:,geo.smap[:,0]],geo.normals)
         kappa_j          =  jnp.einsum('si,...sij,sj->...s',geo.normals,kappa[:,geo.smap[:,1]],geo.normals)

         #cf               = 2*jnp.einsum('...s,s->...s',kappa_i*kappa_j/conductance,1/geo.dists)
         #kappa_ij         = 2*kappa_i * kappa_j/(kappa_i + kappa_j + cf)
         cf = 0
         kappa_ij         = kappa_i * kappa_j/(kappa_i*geo.dists[None,1] + kappa_j*geo.dists[None,0])

        
        
         
         #Normal derivative
         p_sides,p_values = (lambda t: jax.vmap(lambda b: bcs.get_periodic(b, t),0,(None,0))(batch_indices))(t)

  
        
         normal_derivative     = jnp.einsum('bsu,suj->bsj',X[:,geo.N_indices],geo.N_data) + \
                                 jnp.einsum('spj,bp->bsj', geo.N_periodic_data, p_values)
         
         tangential_derivative = jnp.einsum('bsu,suj->bsj',X[:,geo.T_indices],geo.T_data) + \
                                 jnp.einsum('spj,bp->bsj', geo.T_periodic_data, p_values)
         
         #print(tangential_derivative
               
         print(tangential_derivative + normal_derivative)
         
         quit()


         non_orthogonal_contribution = geo.dists[0]*geo.dists[1]*jnp.einsum('si,bsij,bsj->bs',geo.normals,kappa[:,geo.smap[:,1]]-kappa[:,geo.smap[:,0]],tangential_derivative)

         T_boundary     = (X[:,geo.smap[:,0]]*kappa_i*geo.dists[1]+X[:,geo.smap[:,1]]*kappa_j*geo.dists[0] + non_orthogonal_contribution)/(kappa_i*geo.dists[1] + kappa_j*geo.dists[0])         

         contribution_i   = jnp.einsum('...s,sd,s->...sd',T_boundary*kappa_i,geo.normals,geo.areas)
         contribution_j   = jnp.einsum('...s,sd,s->...sd',T_boundary*kappa_j,geo.normals,geo.areas)
         J                = J.at[:,geo.smap[:,0],:].add(-contribution_i).at[:,geo.smap[:,1],:].add(contribution_j)

         #Compute side fluxes (internal)
         P_internal = -jnp.einsum('b...,b...->b...',kappa_ij[:,compute_side_flux],X[:,geo.smap[compute_side_flux,1]] - X[:,geo.smap[compute_side_flux,0]]) #W/mK

        
      
         #Periodic
         p_sides,p_values = (lambda t: jax.vmap(lambda b: bcs.get_periodic(b, t),0,(None,0))(batch_indices))(t)
       
         contribution     = jnp.einsum('...s,...s,s,sd->...sd',0.5*kappa_ij[:,p_sides],p_values,geo.areas[p_sides],geo.normals[p_sides]) 
         J                = J.at[:,geo.smap[p_sides,0],:].add(-contribution)
         J                = J.at[:,geo.smap[p_sides,1],:].add(-contribution) 
         P                = jnp.zeros((batch_size,N))
         bulk_d           = jnp.einsum('...s,s->...s',kappa_ij,geo.areas)
         tmp              = jnp.einsum('...s,...s->...s',bulk_d[:,p_sides],p_values)
         p_elems          = geo.smap[p_sides]
         P                = P.at[:,p_elems[:,0]].add( tmp)
         P                = P.at[:,p_elems[:,1]].add(-tmp)

         #Normal contribution
         kappa_effective  = jnp.einsum('...s,...s,s->...',kappa_ij[:,p_sides],p_values**2,geo.areas[p_sides]) - jnp.einsum('...c,...c->...',X,P)

         #Tangential contribution

         
         #Thermalizing boundaries
         thermo_sides     = bcs.get_temperature_sides()
         thermo_values    = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_temperature_values(b,s,t))(jnp.arange(len(thermo_sides))))(batch_indices)
         side_normals     = geo.boundary_normals[thermo_sides]
         thermo_elems     = geo.boundary_sides[thermo_sides]
         kappa_b          = jnp.einsum('si,...sij,sj->...s',side_normals,kappa[:,thermo_elems],side_normals)
         contribution     = jnp.einsum('...s,...s,sd,s->...sd',thermo_values,kappa_b,side_normals,geo.boundary_areas[thermo_sides])
         J                = J.at[:,thermo_elems,:].add(-contribution)

         #This is in case for thermalizing boundaries
         J_boundary       = jnp.einsum('...s,...s,s->...s',thermo_values-X[:,thermo_elems],kappa_b,1/geo.boundary_dists[thermo_sides])
         kappa_effective += jnp.absolute(jnp.einsum('s,...s->...s',geo.boundary_areas[thermo_sides],J_boundary)).sum(axis=1)/2
         P_boundary       = P_boundary.at[:,thermo_sides].set(-J_boundary)
         T_boundary       = T_boundary.at[:,thermo_sides].set(thermo_values)

         #Flux boundaries
         flux_sides       = bcs.get_flux_sides()
         flux_elems       = geo.boundary_sides[flux_sides]  
         kappa_b          = jnp.einsum('si,...sij,sj->...s',geo.boundary_normals[flux_sides],kappa[:,flux_elems],geo.boundary_normals[flux_sides])
         if len(flux_sides) > 0:
          #flux_values      = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_flux_values(b,s,t,Tb[b,s]))(jnp.arange(len(flux_sides))))(jnp.arange(batch_size))
          flux_values      = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_flux_values(batch_indices[b],s,t,Tb[b,s]))(jnp.arange(len(flux_sides))))(batch_1D)
          #else:
          #flux_values      = jnp.zeros((batch_size,len(flux_sides)))
         
          #Old
           #T_boundary       = X[:,flux_elems] - geo.boundary_dists[flux_sides][jnp.newaxis,:] * flux_values/kappa_b
        
          T_boundary       = T_boundary.at[:,flux_sides].set(Tb)
          contribution     = jnp.einsum('...s,sd,s...->...sd',Tb*kappa_b,geo.boundary_normals[flux_sides],geo.boundary_areas[flux_sides])
          J                = J.at[:,flux_elems,:].add(-contribution)
          #P_boundary       = P_boundary.at[:,flux_sides].set(flux_values*geo.boundary_areas[flux_sides])
          P_boundary       = P_boundary.at[:,flux_sides].set(flux_values)

         
         #Robin boundary conditions---
         robin_sides      = bcs.get_robin_sides()
         #robin_h,robin_T  = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_robin_values(b,s,t))(jnp.arange(len(robin_sides))))(jnp.arange(batch_size))
         robin_h,robin_T  = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_robin_values(b,s,t))(jnp.arange(len(robin_sides))))(batch_indices)

         robin_elems      = geo.boundary_sides[robin_sides]
    
         side_normals     = geo.boundary_normals[robin_sides]
         kappa_b          = jnp.einsum('si,...sij,sj->...s',side_normals,kappa[:,robin_elems],side_normals)  
        
         gamma            = jnp.einsum('...s,s,...s->...s',robin_h,geo.boundary_dists[robin_sides],1/kappa_b)

     
         T_boundary_robin = (X[:,robin_elems] + gamma*robin_T)/(1+gamma)
         contribution     = jnp.einsum('...s,...s,sd,s->...sd',T_boundary_robin,kappa_b,side_normals,geo.boundary_areas[robin_sides])
         J                = J.at[:,robin_elems,:].add(-contribution)


         #flux_values      = robin_h*(T_boundary_robin-robin_T)
         flux_values      = robin_h*(X[:,robin_elems]-robin_T)/(gamma+1)

        
         #P_boundary       = P_boundary.at[:,robin_sides].set(flux_values*geo.boundary_areas[robin_sides])
         P_boundary       = P_boundary.at[:,robin_sides].set(flux_values)
         T_boundary       = T_boundary.at[:,robin_sides].set(T_boundary_robin)

         J = J/geo.V[jnp.newaxis,:,jnp.newaxis]
        
         return J,kappa_effective,P_boundary,P_internal,T_boundary
        
        
        T = T.reshape((NT_save,batch_size,-1))
        TB = TB.reshape((NT_save,batch_size,-1))


        kappa = jax.vmap(
         lambda t:
         jax.vmap(
            lambda b:
                jax.vmap(
                    lambda i:
                        thermal_conductivity(batch_indices[b],i,T[t, b, i],t)
                )(geo.cell_id)
         )(batch_1D)
        )(jnp.arange(NT_save))

        
        #TODO: this needs to be batched
        cond = jax.vmap(conductance, in_axes=(0, 0))(T, jnp.arange(NT_save))

        J,kappa_effective,P_boundary,P_internal,T_boundary = jax.vmap(get_flux)(T,TB,kappa,cond,jnp.arange(NT_save))

        scalar_output = {'kappa_effective':kappa_effective[0].reshape(batch_map,order='F')} #Only return the initial time step


        output = Fields()
        output = output.add_field('Temperature',T.reshape((*batch_map,NT_save,*geo.grid),order='F') ,units='K',batch_map=batch_map,time_stamps=saveat)
        output = output.add_field('Heat_source',H.reshape((*batch_map,NT_save,*geo.grid),order='F'),units='W/m^3',batch_map=batch_map,time_stamps=saveat)
        output = output.add_field('Heat_flux',J.reshape((*batch_map,NT_save,*geo.grid,geo.dim),order='F'),units='W/m^2',batch_map=batch_map,time_stamps=saveat)
        output = output.add_field('Thermal_conductivity',kappa.reshape((*batch_map,NT_save,*geo.grid,geo.dim,geo.dim),order='F'),units='W/m/K',batch_map=batch_map,time_stamps=saveat)
        output = output.add_field('Boundary_flux',P_boundary.reshape((*batch_map,NT_save,-1),order='F'),units='W/m^2',surface=True,batch_map=batch_map,time_stamps=saveat)
        output = output.add_field('Internal_flux',P_internal.reshape((*batch_map,NT_save,-1),order='F'),units='W/m^2',surface=True,batch_map=batch_map,time_stamps=saveat)
        output = output.add_field('Boundary_temperature',T_boundary.reshape((*batch_map,NT_save,-1),order='F'),units='K',surface=True,batch_map=batch_map,time_stamps=saveat)


        return output,scalar_output,stats
    
   
