from dataclasses import fields
import equinox as eqx
import jax
from jax import numpy as jnp
from typing import List,Callable
import numpy as np
from functools import partial
from typing import List
from interpax import interp2d
from jax.experimental import sparse



def shift(arr, shift, axis, fill_value=False):
    arr = np.asarray(arr)
    result = np.full_like(arr, fill_value)

    if shift == 0:
        return arr.copy()

    src = [slice(None)] * arr.ndim
    dst = [slice(None)] * arr.ndim

    if shift > 0:
        src[axis] = slice(0, -shift)
        dst[axis] = slice(shift, None)
    else:
        src[axis] = slice(-shift, None)
        dst[axis] = slice(0, shift)

    result[tuple(dst)] = arr[tuple(src)]
    return result

class Geometry2D(eqx.Module):
  
   
    N                  : int
    nDOFs              : int
    grid               : List[int]
    size               : np.array
    x_nodes            : jax.Array
    y_nodes            : jax.Array
    x_centroids        : jax.Array
    y_centroids        : jax.Array
    dim                : int = 2
    mask               : jax.Array
    cell_id            : jax.Array
    V                  : jax.Array
    boundary_centroids : np.array
    boundary_normals   : jax.Array
    boundary_sides     : jax.Array
    boundary_areas     : jax.Array
    boundary_dists     : jax.Array
    smap               : jax.Array
    normals            : jax.Array
    centroids          : jax.Array
    face_centroids     : jax.Array
    areas              : jax.Array
    dists              : jax.Array
    periodic           : np.array
   
    T_indices          : jax.Array
    T_data             : jax.Array
    T_periodic_data    : jax.Array
    N_data             : jax.Array
    N_indices          : jax.Array
    N_periodic_data    : jax.Array


    
    def __init__(self,x_nodes,y_nodes,periodic=[False,False],\
                 domain = None):
      
        #Get grid and size
        self.x_nodes = x_nodes
        self.y_nodes = y_nodes

        #Nodes in Column-major order (Fortran-style)
        X, Y = np.meshgrid(x_nodes, y_nodes, indexing="ij")

        #Update this
        dx = jnp.diff(x_nodes)
        dy = jnp.diff(y_nodes)
        #------------------
       

        if jnp.any(dx <= 0) or jnp.any(dy <= 0):
          raise ValueError("Grid nodes must be strictly increasing along each axis.")

        self.grid = [len(dx), len(dy)]
        self.size = [dx.sum(), dy.sum()]
        Nx, Ny = self.grid
        self.N = Nx * Ny

        #-----------------
        self.periodic = periodic
                


        I_center = np.arange(Nx*Ny).reshape((Nx,Ny), order="F")
       
     
        I_left   = np.roll(I_center, shift=+1, axis=0)#.flatten(order="F")  # x-1
        I_right  = np.roll(I_center, shift=-1, axis=0)#.flatten(order="F")  # x+1
        I_back   = np.roll(I_center, shift=+1, axis=1)#.flatten(order="F")  # y-1
        I_front  = np.roll(I_center, shift=-1, axis=1)#.flatten(order="F")  # y+1

        I_front_right = np.roll(I_front, shift=-1, axis=0)#.flatten(order="F")  # y+1,x+1
        I_front_left  = np.roll(I_front, shift=+1, axis=0)#.flatten(order="F")  # y+1,x-1
        I_back_right  = np.roll(I_back, shift=-1, axis=0)#.flatten(order="F")   # y-1,x+1
        I_back_left   = np.roll(I_back, shift=+1, axis=0)#.flatten(order="F")   # y-1,x-1

        I_center = I_center.flatten(order="F")
        I_left   = I_left.flatten(order="F")
        I_right  = I_right.flatten(order="F")
        I_back   = I_back.flatten(order="F")
        I_front  = I_front.flatten(order="F")

        I_front_right = I_front_right.flatten(order="F")
        I_front_left  = I_front_left.flatten(order="F")
        I_back_right  = I_back_right.flatten(order="F")
        I_back_left   = I_back_left.flatten(order="F")



      
        # Centroid coordinates (midpoint of each cell)
        self.x_centroids = (x_nodes[:-1] + x_nodes[1:]) / 2
        self.y_centroids = (y_nodes[:-1] + y_nodes[1:]) / 2

        X, Y = jnp.meshgrid(self.x_centroids, self.y_centroids, indexing="ij")
       

        centroids = jnp.stack((X.ravel(order="F"),
                               Y.ravel(order="F")), axis=-1)
       
      
   
        #Setting up maps----------------
        mask = jnp.ones((self.N,), dtype=bool)
        if domain:
         mask = np.logical_and(jax.vmap(domain)(centroids), mask)

        
        # flat (Ix-fastest) ➜ (Nx,Ny)
        self.mask = mask.reshape(self.grid, order="F")

       
        #Build maps
        self.nDOFs = int(self.mask.sum())
        
        #Compute volumes
        V = (dx[:, None] * dy[None, :])[self.mask]
        
        
        self.V = V

        #Shift along increasing x (downward of index 0 in array space and rightward in physics space)
        mask = np.logical_and(self.mask,shift(self.mask,shift=-1,axis=0,
                                               fill_value=True if periodic[0] else False))
        
    
        Nm = np.sum(mask) 

        #smap = jnp.vstack((I_center[mask],I_right[mask])).T  #(Nm,2)
        smap = jnp.vstack((I_center,I_right)).T  #(Nm,2)
       
        
        X_faces = x_nodes[1:]                     # (Nx,)
        Y_faces = (y_nodes[:-1] + y_nodes[1:]) / 2  # (Ny,)

        # Make 2D meshgrid with same convention
        Xf, Yf = jnp.meshgrid(X_faces, Y_faces, indexing="ij")

        # Flatten in Fortran order (x fastest)
        face_centroids = jnp.stack((
          Xf.ravel(order="F"),
          Yf.ravel(order="F")
        ), axis=-1)

    
        # Apply mask consistently
        face_centroids = face_centroids[mask.ravel(order="F")]
       
        #areas = (dy[Iy[mask]]).reshape(-1)
        #areas = dy
        #print(areas)
        # Broadcast to (Nx, Ny)
        areas_x = jnp.tile(dy[None, :], (Nx, 1))

        # Flatten in Fortran order (x fastest)
        areas_x = areas_x.ravel(order="F")

        # Apply mask in Fortran order
        areas_x = areas_x[mask.ravel(order="F")]

        areas = areas_x

        
        normals = jnp.tile(jnp.array([1, 0]), (Nm, 1))


        dists_1 = face_centroids[:,0] - centroids[I_center, 0] #because it is along x
        dists_2 = centroids[I_right, 0] - face_centroids[:,0]

        #ADD Periodic distances
        dists_2 = jnp.where(dists_2 > 0, dists_2, dists_2 + self.size[0] * periodic[0])
        dists = jnp.column_stack((dists_1,dists_2)).T


 

        
        #Shift along increasing y (rightward of index 1 in array space and frontward in physics space)
        mask = np.logical_and(
        self.mask,
        shift(self.mask, shift=-1, axis=1, fill_value=True if periodic[1] else False)
        )

        Nm = np.sum(mask) 

        smap = jnp.vstack((smap, jnp.vstack((I_center, I_front)).T))

        # +y faces
        X_faces = (x_nodes[:-1] + x_nodes[1:]) / 2   # (Nx,) midpoints in x
        Y_faces = y_nodes[1:]                        # (Ny,) top face nodes

        # Meshgrid with ij indexing (x fastest)
        Xf, Yf = jnp.meshgrid(X_faces, Y_faces, indexing="ij")

        # Flatten in Fortran order (x fastest)
        face_centroids_along_y = jnp.stack((
            Xf.ravel(order="F"),
            Yf.ravel(order="F")
        ), axis=-1)
        # Apply mask consistently in Fortran order
        face_centroids_along_y = face_centroids_along_y[mask.ravel(order="F")]

       
        face_centroids = jnp.vstack((
        face_centroids,face_centroids_along_y
        ))

        # Areas and distances
        #areas_y = (dx[Ix[mask]]).reshape(-1)

        Dx = dx  # (Nx,)

        # Broadcast along y 
        DX, _ = jnp.meshgrid(Dx, y_nodes[1:], indexing="ij")  # (Nx, Ny)

        # Flatten in Fortran order
        areas_y = DX.ravel(order="F")

        # Apply mask consistently in Fortran order
        areas_y = areas_y[mask.ravel(order="F")]
        areas = jnp.concatenate((areas,areas_y))

        

        dists_1 = face_centroids_along_y[:,1] - centroids[I_center, 1]
        dists_2 = centroids[I_front, 1] - face_centroids_along_y[:,1]

        #ADD Periodic distances
        dists_2 = jnp.where(dists_2 > 0, dists_2, dists_2 + self.size[1] * periodic[1])

        dists_y = jnp.column_stack((dists_1,dists_2)).T
        dists = jnp.concatenate((dists, dists_y), axis=1)

        
        #print(jnp.flipud(mask.T))
        
        # Normals
        normals = jnp.vstack((normals, jnp.tile(jnp.array([0, 1]), (Nm, 1))))

       
        
        #Boundary right
        #Create a mask that is true only for the elements hosting a boundary
        # I = shift(self.mask, shift=-1, axis=0)
        # mask = np.logical_and(self.mask, np.logical_not(I))
        # if periodic[0]:
        #   mask[-1, :] = False

        
        # Nm = np.sum(mask)

        # # Centroids of +x boundary faces
        # boundary_centroids = jnp.stack((
        #     x_nodes[Ix[mask] + 1],                                       # right face node
        #     (y_nodes[Iy[mask]] + y_nodes[Iy[mask] + 1]) / 2,             # mid y
        #     ), axis=-1).reshape(-1, 2)

     
        # # Neighbor indices
        # boundary_sides = I_center[mask]

        # # Areas and distances
        # boundary_areas = (dy[Iy[mask]]).reshape(-1)
        # boundary_dists = (dx[Ix[mask]]/2).reshape(-1)

        # # Normals
        # boundary_normals = jnp.tile(jnp.array([1, 0]), (Nm, 1))

        
        # # Left boundary (−x)
        # I = shift(self.mask, shift=1, axis=0)
        # mask = np.logical_and(self.mask, np.logical_not(I))
        # if periodic[0]:
        #  mask[0, :] = False

        # Nm = np.sum(mask) 
        

        # # Face centroids for −x boundary
        # boundary_centroids = jnp.vstack((
        #  boundary_centroids,
        #  jnp.stack((
        #   x_nodes[Ix[mask]],                                      # left face node
        #   (y_nodes[Iy[mask]] + y_nodes[Iy[mask] + 1]) / 2,        # mid y
        #  ), axis=-1).reshape(-1, 2)
        # ))

        # # Neighbor indices
        # boundary_sides = jnp.concatenate((boundary_sides, I_center[mask]))

        # # Areas and distances
        # boundary_areas = jnp.concatenate((boundary_areas,
        #                           (dy[Iy[mask]]).reshape(-1)))
        # boundary_dists = jnp.concatenate((boundary_dists,
        #                           (dx[Ix[mask]] / 2).reshape(-1)))

        # # Normals
        # boundary_normals = jnp.concatenate((
        #  boundary_normals,
        #  jnp.tile(jnp.array([-1, 0]), (Nm, 1))
        #  ), axis=0)

       
        # # +y boundary (front)
        # I = shift(self.mask,shift=-1,axis=1)
        # mask   = np.logical_and(self.mask,np.logical_not(I))
        # if periodic[1]: mask[:,-1] = False

        # Nm = np.sum(mask)

    
        # boundary_centroids = jnp.vstack((
        #   boundary_centroids,
        #  jnp.stack((
        # (x_nodes[Ix[mask]] + x_nodes[Ix[mask] + 1]) / 2,   # mid x
        # y_nodes[Iy[mask] + 1],                             # face at top node
        # ), axis=-1).reshape(-1, 2)
        # ))

        # boundary_sides = jnp.concatenate((boundary_sides, I_center[mask]))

        # boundary_areas = jnp.concatenate((
        #     boundary_areas,
        #     (dx[Ix[mask]]).reshape(-1)
        # ))

        # boundary_dists = jnp.concatenate((
        #  boundary_dists,
        # (dy[Iy[mask]] / 2).reshape(-1)
        # ))

        # boundary_normals = jnp.concatenate((
        #  boundary_normals,
        #  jnp.tile(jnp.array([0, 1]), (Nm, 1))
        # ), axis=0)


        # #Boundary back
        # I = shift(self.mask,shift=1,axis=1)
        # mask   = np.logical_and(self.mask,np.logical_not(I))
        # if periodic[1]: mask[:,0] = False

        # Nm = np.sum(mask) 
        
        # boundary_centroids = jnp.vstack((
        #    boundary_centroids,
        #   jnp.stack((
        #   (x_nodes[Ix[mask]] + x_nodes[Ix[mask] + 1]) / 2,   # mid x
        #   y_nodes[Iy[mask]],                                # face at bottom node
        #  ), axis=-1).reshape(-1, 2)
        # ))

        # boundary_sides = jnp.concatenate((boundary_sides, I_center[mask]))

        # boundary_areas = jnp.concatenate((
        #  boundary_areas,
        #  (dx[Ix[mask]]).reshape(-1)
        # ))
        # boundary_dists = jnp.concatenate((
        # boundary_dists,
        # (dy[Iy[mask]] / 2).reshape(-1)
        # ))

        # boundary_normals = jnp.concatenate((
        #  boundary_normals,
        #  jnp.tile(jnp.array([0, -1]), (Nm, 1))
        # ), axis=0)

        #Placeholder
        boundary_centroids = []
        boundary_sides     = jnp.empty((0,),dtype=int)
        boundary_areas     = jnp.empty((0,),dtype=float)
        boundary_normals   = jnp.empty((0, 2),dtype=float)
        boundary_dists     = jnp.empty((0,),dtype=float)

        self.boundary_centroids = boundary_centroids
        self.boundary_normals = boundary_normals 
        self.boundary_areas = boundary_areas 
        self.boundary_dists = boundary_dists 
        self.boundary_sides = boundary_sides
      

        self.normals = normals 
        self.face_centroids = face_centroids 
        self.areas = areas 
        self.dists = dists 

        self.smap      = smap
        self.centroids = centroids
  
     
        #self.boundary_sides = self.global2local[boundary_sides]
        self.size = np.array(self.size)
        self.periodic = np.array(self.periodic)

    
        #Get indices in F order
        ii, jj = jnp.indices((Nx, Ny), dtype=int)
        self.cell_id = jnp.stack([ii.ravel(order="F"), jj.ravel(order="F")], axis=1)


        #Compute derivative operator
        #Perioedic sides are in periodic coordinates
        s_periodic_y      = np.arange(Ny, Nx + Ny) 
        s_periodic_x      = np.arange(Ny)

        #Sides
        s_right_vertical  = np.arange(Nx - 1, Nx * Ny, Nx)      
        s_top_vertical    = np.arange(Nx * (Ny - 1), Nx * Ny) 
        s_bottom_vertical = np.arange(0, Nx) 
        s_right_horizontal= Nx*Ny + np.arange(Nx - 1, Nx * Ny, Nx)
        s_left_horizontal = Nx*Ny + np.arange(0, Ny*Nx, Ny)
        s_top_horizontal  = Nx*Ny + np.arange(Nx * (Ny - 1), Nx * Ny) 
        
        #Elements
        v_bottom          = np.arange(Nx)                 
        v_left            = np.arange(0, Nx * Ny, Nx)      
        v_top             = np.arange(Nx * (Ny - 1), Nx * Ny)
        v_right           = np.arange(Nx - 1, Nx * Ny, Nx)

      
        
        #Normal derivative
        N_periodic_data = np.zeros((2*Nx*Ny,Nx+Ny,2))
        N_update = lambda d,i,j,a: np.add.at(N_periodic_data, (i,j,d), a/(self.dists[:,i].sum(axis=0)))


        
        #Along x 
        N_indices_x = jnp.column_stack((I_right,I_center))
        tmp            = 1/dists[:,:Nx*Ny].sum(axis=0) 
        N_data_x       = jnp.column_stack((tmp,-tmp))
        N_data_x       = jnp.stack((N_data_x,jnp.zeros_like(N_data_x)),axis=2)

        #Right
        N_update(0,s_right_vertical,s_periodic_x,1)
        
     
       
        N_indices_y    = jnp.column_stack((I_front,I_center))
        tmp            = 1/dists[:,Nx*Ny:].sum(axis=0) 
        N_data_y       = jnp.column_stack((tmp,-tmp))
        N_data_y       = jnp.stack((jnp.zeros_like(N_data_y),N_data_y),axis=2)

        #Front
        N_update(1,s_top_horizontal,s_periodic_y,1)

        self.N_data    = jnp.concatenate((N_data_x,N_data_y),axis=0)
        self.N_indices = jnp.concatenate((N_indices_x,N_indices_y),axis=0)
        self.N_periodic_data = N_periodic_data

       
    
    
        #Tangential derivative 
        
        #Indices
        T_indices_y   = jnp.column_stack((I_front,
                                          I_front_right,
                                          I_back,
                                          I_back_right))
        

        T_indices_x   = jnp.column_stack((I_front_right,
                                          I_right,
                                          I_front_left,
                                          I_left))
        
        self.T_indices = jnp.concatenate((T_indices_y,T_indices_x),axis=0)
      
        #Data
        T_data_y      = 0.25*(jnp.column_stack((self.V[I_front],
                                                self.V[I_front_right],
                                               -self.V[I_back],
                                               -self.V[I_back_right]))/areas[:Nx*Ny,None])

        T_data_y      = jnp.stack((jnp.zeros_like(T_data_y),T_data_y),axis=2)

        T_data_x      = 0.25*(jnp.column_stack((self.V[I_front_right],
                                                self.V[I_right],
                                               -self.V[I_front_left],
                                               -self.V[I_left]))/areas[Nx*Ny:,None])

        T_data_x      = jnp.stack((T_data_x,jnp.zeros_like(T_data_x)),axis=2)

        self.T_data        = jnp.concatenate((T_data_y,T_data_x),axis=0)


      
        #Periodic data
        T_periodic_data = np.zeros((2*Nx*Ny,Nx+Ny,2))   

        T_update = lambda d,i,j,k,a: np.add.at(T_periodic_data, (i,j,d), a*0.25*V[k]/areas[i])

        def T_update(d,i,j,k,a): 

            #if 5 in i and d == 1:
            #    print(j)
            np.add.at(T_periodic_data, (i,j,d), a*0.25*V[k]/areas[i])
            return None

        
        #y-tangent
    
        #Front 
        #print(0)
        T_update(1,s_top_vertical,
                  s_periodic_y,
                  v_bottom, 1)

        #Back 
       
        T_update(1,s_bottom_vertical,
                  s_periodic_y,
                  v_top, 1)

        #Front-right------
        #Right part )
       
       
        T_update(1,s_right_vertical,
                 np.roll(s_periodic_x, -1),
                 np.roll(v_left, -1), -1)
           
        #Front part
      
        T_update(1,s_top_vertical,
                  np.roll(s_periodic_y, -1),
                  np.roll(v_bottom, -1), 1)
           
        #Back-right------
        #Right part 
       
        T_update(1,s_right_vertical,
                    np.roll(s_periodic_x, 1),
                    np.roll(v_left, 1),1)
        
        #TODO the corner
           
          
        #Back part       
          
        T_update(1,s_bottom_vertical,
                      np.roll(s_periodic_y, -1),
                      np.roll(v_top, -1),1)   

       
        #x_tangent -------------------

        #Right
        T_update(0,s_right_horizontal,
               s_periodic_x,
               v_left,1)
        
        #Left
        T_update(0,s_left_horizontal,
               s_periodic_x,
               v_right,1)
               
        #Front right
        # Right part
        T_update(0,s_right_horizontal,
               np.roll(s_periodic_x, -1),
               np.roll(v_left, -1),1)    
        
        
        # Front part
        T_update(0,s_top_horizontal,
               np.roll(s_periodic_y, -1),
               np.roll(v_bottom, -1),1)  
        
      

        # Front left
        # Left part
       
        T_update(0,s_left_horizontal,
               np.roll(s_periodic_x, -1),
               np.roll(v_right, -1),1)
        
        # Front part
        T_update(0,s_top_horizontal,
               np.roll(s_periodic_y, 1),
               np.roll(v_bottom, 1),-1)
        

       

       
        self.T_periodic_data    = T_periodic_data
      

    def select_boundary(self,func):
        """Get select boundaries""" 

        vmax = self.boundary_centroids.max(axis=0)
        vmin = self.boundary_centroids.min(axis=0)

        if isinstance(func,str):
           
           if   func == 'left':
                func = lambda p  : np.isclose(p[0],vmin[0])
           elif func == 'right':   
                func = lambda p  : np.isclose(p[0], vmax[0])
           elif func == 'front':   
                func = lambda p  : np.isclose(p[1],  vmax[1])
           elif func == 'back':   
                func = lambda p  : np.isclose(p[1], vmin[1])
           elif func == 'everywhere':   
                return jnp.arange(len(self.boundary_centroids))
        
        
        #return jax.vmap(func)(self.boundary_centroids).nonzero()[0]
        return func(self.boundary_centroids.T).nonzero()[0]
      
          
    
    def compute_function_on_centroids(self,func):
       """Select specific regions""" 

       out = jax.vmap(func)(self.centroids)

       return jax.tree_map(
        lambda x: x.reshape(self.grid, order="F") if isinstance(x, jnp.ndarray) else x,
       out
       )
    
    def select_internal_boundary(self,func):
       """Get select boundaries""" 

       return func(self.face_centroids.T).nonzero()[0]


    def cell2side(self,func):

        return partial(func,i=self.smap[:,0],j=self.smap[:,1])
    
    def grad_interpolation(self,f):
        """Gradient of the interpolation of a given field f defined at centroids"""

        #method = 'catmull-rom'
        method = 'cubic2'

        period = [
    None if self.periodic[0] * self.size[0] == 0 else self.periodic[0] * self.size[0],
    None if self.periodic[1] * self.size[1] == 0 else self.periodic[1] * self.size[1],
        ] 
        
        interpolator = lambda p: interp2d(*p,self.x_centroids, self.y_centroids, f,method=method,period=period)

        return jax.jit(jax.vmap(jax.grad(interpolator)))(self.centroids).reshape((*self.grid,2),order='F')

    def hessian_interpolation(self,f):
        """Hessian of the interpolation of a given field f defined at centroids"""
        

        period = [
    None if self.periodic[0] * self.size[0] == 0 else self.periodic[0] * self.size[0],
    None if self.periodic[1] * self.size[1] == 0 else self.periodic[1] * self.size[1],
        ] 

      
        #method = 'catmull-rom'
        method = 'cubic2'
        interpolator =  lambda p: interp2d(*p,self.x_centroids, self.y_centroids, f,method=method,period=period)

        return jax.vmap(jax.hessian(interpolator))(self.centroids).reshape((*self.grid,2,2),order='F')
    
    #@eqx.filter_jit
    def convolve_with_kernel(self,
                 kernel: jnp.array,
                 FFT: bool) -> Callable:
       """Convolution operator with a given kernel
         param FFT: if True use FFT-based convolution (faster for large grids and periodic BCs)
     """
       
       if self.periodic[0] and not self.periodic[1]:
          
          return lambda x: jax.scipy.signal.convolve(
            jnp.pad(x, ((self.grid[0], self.grid[0]), (0, 0)), mode='wrap'), kernel, mode='same', method='fft'
        )[self.grid[0]:2*self.grid[0], :]
       
       elif self.periodic[1] and not self.periodic[0]:

          return lambda x: jax.scipy.signal.convolve(
            jnp.pad(x, ((0, 0), (self.grid[1], self.grid[1])), mode='wrap'), kernel, mode='same', method='fft'
        )[:, self.grid[1]:2*self.grid[1]]
       
       elif not self.periodic[1] and not self.periodic[0]:
           
           return lambda x: jax.scipy.signal.convolve(x, kernel, mode='same', method='fft')
       
       elif self.periodic[1] and self.periodic[0]:
    
        if FFT: 
            # Pre-compute the shifted FFT kernel HERE, outside the lambda
            kernel_shifted_FFT = jnp.fft.fftn(jnp.fft.ifftshift(kernel))
            
            # Return lambda that uses the pre-computed FFT kernel
            return lambda x: jnp.real(jnp.fft.ifftn(jnp.fft.fftn(x) * kernel_shifted_FFT))

        else:

         return lambda x: jax.scipy.signal.convolve(
            jnp.pad(x, ((self.grid[0], self.grid[0]), (self.grid[1], self.grid[1])), mode='wrap'), kernel, mode='same', method='fft'
        )[self.grid[0]:2*self.grid[0], self.grid[1]:2*self.grid[1]]

       else :   
         raise NotImplementedError("Convolution not implemented for this type of periodicity")
       

              



    

