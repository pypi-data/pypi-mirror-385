import equinox as eqx
import jax
from jax import numpy as jnp
from typing import List,Callable
import numpy as np
from functools import partial
from typing import List
from interpax import interp3d


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

class Geometry3D(eqx.Module):
  
   
   
    N                  : int
    nDOFs              : int
    grid               : List[int]
    size               : List[float]
    center             : np.array
    x_nodes            : jax.Array
    y_nodes            : jax.Array
    z_nodes            : jax.Array
    x_centroids        : jax.Array
    y_centroids        : jax.Array
    z_centroids        : jax.Array
    dim                : int = 3
    mask               : jax.Array
    cell_id            : jax.Array
    V                  : jax.Array
    boundary_centroids : jax.Array
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
    local2global       : jax.Array
    global2local       : jax.Array
    periodic           : List


    def __init__(self,x_nodes,y_nodes,z_nodes,periodic=[False,False,False],\
                 domain = None):
      
        #Get grid and size
        self.x_nodes = x_nodes
        self.y_nodes = y_nodes
        self.z_nodes = z_nodes

        self.center = np.array([(x_nodes[0] + x_nodes[-1]) / 2,
                                  (y_nodes[0] + y_nodes[-1]) / 2,
                                    (z_nodes[0] + z_nodes[-1]) / 2
                                  ])

        #Nodes in Column-major order (Fortran-style)
        X, Y, Z = np.meshgrid(x_nodes, y_nodes, z_nodes, indexing="ij")


        dx = jnp.diff(x_nodes)
        dy = jnp.diff(y_nodes)
        dz = jnp.diff(z_nodes)

        if jnp.any(dx <= 0) or jnp.any(dy <= 0) or jnp.any(dz <= 0):
          raise ValueError("Grid nodes must be strictly increasing along each axis.")

        self.grid = [len(dx), len(dy), len(dz)]
      

        self.size = [jnp.ptp(x_nodes), jnp.ptp(y_nodes), jnp.ptp(z_nodes)]
        
        Nx, Ny, Nz = self.grid
        self.N = Nx * Ny * Nz
       
        #-----------------
        self.periodic = periodic
                

      
        I_center = np.arange(Nx*Ny*Nz).reshape((Nx,Ny,Nz), order="F")
        I_left   = np.roll(I_center, shift=+1, axis=0)  # x-1
        I_right  = np.roll(I_center, shift=-1, axis=0)  # x+1
        I_back   = np.roll(I_center, shift=+1, axis=1)  # y-1
        I_front  = np.roll(I_center, shift=-1, axis=1)  # y+1
        I_bottom = np.roll(I_center, shift=+1, axis=2)  # z-1
        I_top    = np.roll(I_center, shift=-1, axis=2)  # z+1

        
        Ix, Iy, Iz = np.indices((Nx, Ny, Nz))
       
       # Centroid coordinates (midpoint of each cell)
        self.x_centroids = (x_nodes[:-1] + x_nodes[1:]) / 2
        self.y_centroids = (y_nodes[:-1] + y_nodes[1:]) / 2
        self.z_centroids = (z_nodes[:-1] + z_nodes[1:]) / 2

        X, Y, Z = jnp.meshgrid(self.x_centroids, self.y_centroids, self.z_centroids, indexing="ij")

        centroids = jnp.stack((X.ravel(order="F"),
                               Y.ravel(order="F"),
                               Z.ravel(order="F")), axis=-1)
        
  
        #---------------------------------------------------------------------
     
    
        #Setting up maps----------------
        mask = jnp.ones((self.N,), dtype=bool)
        if domain:
         mask = np.logical_and(jax.vmap(domain)(centroids), mask)


        
        # flat (Ix-fastest) ➜ (Nx,Ny,Nz)
        self.mask = mask.reshape(self.grid, order="F")

        #Build maps
        self.nDOFs = int(self.mask.sum())
        
        
        #Compute volumes
        V = dx[:, None, None] * dy[None, :, None] * dz[None, None, :]

      
        
        #Shift along increasing x (downward of index 0 in array space and rightward in physics space)
        mask = np.logical_and(self.mask,shift(self.mask,shift=-1,axis=0,
                                               fill_value=True if periodic[0] else False))
        

        Nm = np.sum(mask) 

        smap = jnp.vstack((I_center[mask],I_right[mask])).T  #(Nm,2)
       
      
        #face centroids
        face_centroids = jnp.stack((
                x_nodes[Ix[mask] + 1],                                     # face at right node
               (y_nodes[Iy[mask]] + y_nodes[Iy[mask] + 1]) / 2,            # mid y
               (z_nodes[Iz[mask]] + z_nodes[Iz[mask] + 1]) / 2             # mid z
                ), axis=-1).reshape(-1, 3)

        areas = (dy[Iy[mask]] * dz[Iz[mask]]).reshape(-1)
        #dists = (dx[Ix[mask]]).reshape(-1)
        normals = jnp.tile(jnp.array([1, 0, 0]), (Nm, 1))
       

        dists_1 = face_centroids[:,0] - centroids[I_center[mask], 0]
        dists_2 =  centroids[I_right[mask], 0] - face_centroids[:,0]
         #ADD Periodic distances
        dists_2 = jnp.where(dists_2 > 0, dists_2, dists_2 + self.size[0] * periodic[0])
        dists = jnp.column_stack((dists_1,dists_2)).T 


        #Shift along increasing y (rightward  of index 1 in array space and frontward in physics space)
        mask = np.logical_and(
        self.mask,
        shift(self.mask, shift=-1, axis=1, fill_value=True if periodic[1] else False)
        )

        Nm = np.sum(mask) 

        smap = jnp.vstack((smap, jnp.vstack((I_center[mask], I_front[mask])).T))

        # Face centroids for +y faces
        face_centroids_along_y =  jnp.stack((
         (x_nodes[Ix[mask]] + x_nodes[Ix[mask] + 1]) / 2,   # mid x
         y_nodes[Iy[mask] + 1],                             # face at top node
         (z_nodes[Iz[mask]] + z_nodes[Iz[mask] + 1]) / 2    # mid z
        ), axis=-1).reshape(-1, 3)
        

        face_centroids = jnp.vstack((
        face_centroids,
        face_centroids_along_y
       ))

        # Areas and distances
        areas = jnp.concatenate((areas, (dx[Ix[mask]] * dz[Iz[mask]]).reshape(-1)))
        #dists = jnp.concatenate((dists, dy[Iy[mask]].reshape(-1)))

        dists_1 = face_centroids_along_y[:,1] - centroids[I_center[mask], 1]
        dists_2 = centroids[I_front[mask], 1] - face_centroids_along_y[:,1]
          #ADD Periodic distances
        dists_2 = jnp.where(dists_2 > 0, dists_2, dists_2 + self.size[1] * periodic[1])
        dists_y = jnp.column_stack((dists_1,dists_2)).T
        dists = jnp.concatenate((dists, dists_y), axis=1)

        # Normals
        normals = jnp.vstack((normals, jnp.tile(jnp.array([0, 1, 0]), (Nm, 1))))

      

        #Shift along increasing z (upward of index 2 in array space and fup in physics space)
        mask = np.logical_and(
        self.mask,
        shift(self.mask, shift=-1, axis=2, fill_value=True if periodic[2] else False)
        )

        Nm = np.sum(mask) 

        smap = jnp.vstack((smap, jnp.vstack((I_center[mask], I_top[mask])).T))

        # Face centroids for +z faces
        face_centroids_along_z =   jnp.stack((
         (x_nodes[Ix[mask]] + x_nodes[Ix[mask] + 1]) / 2,   # mid x
         (y_nodes[Iy[mask]] + y_nodes[Iy[mask] + 1]) / 2,   # mid y
         z_nodes[Iz[mask] + 1]                              # face at top node
        ), axis=-1).reshape(-1, 3)
        

        face_centroids = jnp.vstack((
          face_centroids,face_centroids_along_z
         ))

        # Areas and distances
        areas = jnp.concatenate((areas, (dx[Ix[mask]] * dy[Iy[mask]]).reshape(-1)))
        #dists = jnp.concatenate((dists, dz[Iz[mask]].reshape(-1)))

        dists_1 = face_centroids_along_z[:,2] - centroids[I_center[mask], 2]
        dists_2 = centroids[I_top[mask], 2] - face_centroids_along_z[:,2]
        #ADD Periodic distances
        dists_2 = jnp.where(dists_2 > 0, dists_2, dists_2 + self.size[2] * periodic[2])
        dists_z = jnp.column_stack((dists_1,dists_2)).T
        dists = jnp.concatenate((dists, dists_z), axis=1)

        # Normals
        normals = jnp.vstack((normals, jnp.tile(jnp.array([0, 0, 1]), (Nm, 1))))

        
        #Boundary right
        #Create a mask that is true only for the elements hosting a boundary
        I = shift(self.mask, shift=-1, axis=0)
        mask = np.logical_and(self.mask, np.logical_not(I))
        if periodic[0]:
          mask[-1, :, :] = False
       
        Nm = np.sum(mask)

        # Centroids of +x boundary faces
        boundary_centroids = jnp.stack((
            x_nodes[Ix[mask] + 1],                                       # right face node
            (y_nodes[Iy[mask]] + y_nodes[Iy[mask] + 1]) / 2,             # mid y
            (z_nodes[Iz[mask]] + z_nodes[Iz[mask] + 1]) / 2              # mid z
            ), axis=-1).reshape(-1, 3)

        # Neighbor indices
        boundary_sides = I_center[mask]

        # Areas and distances
        boundary_areas = (dy[Iy[mask]] * dz[Iz[mask]]).reshape(-1)
        boundary_dists = (dx[Ix[mask]] / 2).reshape(-1)

        # Normals
        boundary_normals = jnp.tile(jnp.array([1, 0, 0]), (Nm, 1))

        
        # Left boundary (−x)
        I = shift(self.mask, shift=1, axis=0)
        mask = np.logical_and(self.mask, np.logical_not(I))
        if periodic[0]:
         mask[0, :, :] = False

        Nm = np.sum(mask) 
        

        # Face centroids for −x boundary
        boundary_centroids = jnp.vstack((
         boundary_centroids,
         jnp.stack((
          x_nodes[Ix[mask]],                                      # left face node
          (y_nodes[Iy[mask]] + y_nodes[Iy[mask] + 1]) / 2,        # mid y
          (z_nodes[Iz[mask]] + z_nodes[Iz[mask] + 1]) / 2         # mid z
         ), axis=-1).reshape(-1, 3)
        ))

        # Neighbor indices
        boundary_sides = jnp.concatenate((boundary_sides, I_center[mask]))

        # Areas and distances
        boundary_areas = jnp.concatenate((boundary_areas,
                                  (dy[Iy[mask]] * dz[Iz[mask]]).reshape(-1)))
        boundary_dists = jnp.concatenate((boundary_dists,
                                  (dx[Ix[mask]] / 2).reshape(-1)))

        # Normals
        boundary_normals = jnp.concatenate((
         boundary_normals,
         jnp.tile(jnp.array([-1, 0, 0]), (Nm, 1))
         ), axis=0)

       
        # +y boundary (front)
        I = shift(self.mask,shift=-1,axis=1)
        mask   = np.logical_and(self.mask,np.logical_not(I))
        if periodic[1]: mask[:,-1,:] = False
        

        Nm = np.sum(mask) 
       

    
        boundary_centroids = jnp.vstack((
          boundary_centroids,
         jnp.stack((
        (x_nodes[Ix[mask]] + x_nodes[Ix[mask] + 1]) / 2,   # mid x
        y_nodes[Iy[mask] + 1],                             # face at top node
        (z_nodes[Iz[mask]] + z_nodes[Iz[mask] + 1]) / 2    # mid z
        ), axis=-1).reshape(-1, 3)
        ))

        boundary_sides = jnp.concatenate((boundary_sides, I_center[mask]))

        boundary_areas = jnp.concatenate((
            boundary_areas,
            (dx[Ix[mask]] * dz[Iz[mask]]).reshape(-1)
        ))

        boundary_dists = jnp.concatenate((
         boundary_dists,
        (dy[Iy[mask]] / 2).reshape(-1)
        ))

        boundary_normals = jnp.concatenate((
         boundary_normals,
         jnp.tile(jnp.array([0, 1, 0]), (Nm, 1))
        ), axis=0)


        #Boundary back
        I = shift(self.mask,shift=1,axis=1)
        mask   = np.logical_and(self.mask,np.logical_not(I))
        if periodic[1]: mask[:,0,:] = False

        Nm = np.sum(mask) 
        
        boundary_centroids = jnp.vstack((
           boundary_centroids,
          jnp.stack((
          (x_nodes[Ix[mask]] + x_nodes[Ix[mask] + 1]) / 2,   # mid x
          y_nodes[Iy[mask]],                                # face at bottom node
          (z_nodes[Iz[mask]] + z_nodes[Iz[mask] + 1]) / 2   # mid z
         ), axis=-1).reshape(-1, 3)
        ))

        boundary_sides = jnp.concatenate((boundary_sides, I_center[mask]))

        boundary_areas = jnp.concatenate((
         boundary_areas,
         (dx[Ix[mask]] * dz[Iz[mask]]).reshape(-1)
        ))
        boundary_dists = jnp.concatenate((
        boundary_dists,
        (dy[Iy[mask]] / 2).reshape(-1)
        ))

        boundary_normals = jnp.concatenate((
         boundary_normals,
         jnp.tile(jnp.array([0, -1, 0]), (Nm, 1))
        ), axis=0)

        
        
        # +z boundary (top)
        I = shift(self.mask, shift=-1, axis=2)
        mask = np.logical_and(self.mask, np.logical_not(I))
        if periodic[2]:
          mask[:, :, -1] = False

        Nm = np.sum(mask)

        boundary_centroids = jnp.vstack((
           boundary_centroids,
           jnp.stack((
          (x_nodes[Ix[mask]] + x_nodes[Ix[mask] + 1]) / 2,   # mid x
          (y_nodes[Iy[mask]] + y_nodes[Iy[mask] + 1]) / 2,   # mid y
          z_nodes[Iz[mask] + 1]                              # top node
          ), axis=-1).reshape(-1, 3)
        ))

        boundary_sides = jnp.concatenate((boundary_sides, I_center[mask]))

        boundary_areas = jnp.concatenate((
          boundary_areas,
          (dx[Ix[mask]] * dy[Iy[mask]]).reshape(-1)
        ))
        boundary_dists = jnp.concatenate((
          boundary_dists,
          (dz[Iz[mask]] / 2).reshape(-1)
        ))

        boundary_normals = jnp.concatenate((
         boundary_normals,
         jnp.tile(jnp.array([0, 0, 1]), (Nm, 1))
        ), axis=0)

        #Boundary bottom
        # -z boundary (bottom)
        I = shift(self.mask, shift=1, axis=2)
        mask = np.logical_and(self.mask, np.logical_not(I))
        if periodic[2]:
          mask[:, :, 0] = False

        Nm = np.sum(mask) 
  
        boundary_centroids = jnp.vstack((
         boundary_centroids,
        jnp.stack((
         (x_nodes[Ix[mask]] + x_nodes[Ix[mask] + 1]) / 2,   # mid x
         (y_nodes[Iy[mask]] + y_nodes[Iy[mask] + 1]) / 2,   # mid y
         z_nodes[Iz[mask]]                                  # bottom node
         ), axis=-1).reshape(-1, 3)
        ))

        boundary_sides = jnp.concatenate((boundary_sides, I_center[mask]))

        boundary_areas = jnp.concatenate((
         boundary_areas,
        (dx[Ix[mask]] * dy[Iy[mask]]).reshape(-1)
        ))

        boundary_dists = jnp.concatenate((
          boundary_dists,
         (dz[Iz[mask]] / 2).reshape(-1)
        ))

        boundary_normals = jnp.concatenate((
           boundary_normals,
           jnp.tile(jnp.array([0, 0, -1]), (Nm, 1))
        ), axis=0)

        
    
        self.boundary_centroids = boundary_centroids
        self.boundary_normals = boundary_normals 
        self.boundary_areas = boundary_areas 
        self.boundary_dists = boundary_dists 
      

        self.normals = normals 
        self.face_centroids = face_centroids 
        self.areas = areas 
        self.dists = dists 
  
      
        f_mask = np.ravel(self.mask, order='F')
        self.local2global = np.ravel(I_center, order='F')[f_mask]
        self.global2local = (jnp.ones(self.N, dtype=int)
                     .at[self.local2global].set(jnp.arange(self.nDOFs)))
        self.centroids = centroids[f_mask]
        self.V = jnp.ravel(V, order='F')[f_mask]
        self.boundary_sides = self.global2local[boundary_sides]
        self.smap = self.global2local[smap]
        self.size = np.array(self.size)
        self.periodic = np.array(self.periodic)
        self.boundary_centroids = np.array(self.boundary_centroids)
    

         #Get indices in F order
        ii, jj, kk = jnp.indices((Nx, Ny, Nz), dtype=int)  
        self.cell_id = jnp.stack([ii.ravel(order="F"), jj.ravel(order="F"), kk.ravel(order="F")], axis=1)

    def select_boundary(self,func):
        """Get select boundaries""" 

        vmax = self.boundary_centroids.max(axis=0)
        vmin = self.boundary_centroids.min(axis=0)

        if isinstance(func,str):
           if   func == 'left':
                func = lambda p  : jnp.isclose(p[0],vmin[0])
           elif func == 'right':   
                func = lambda p  : jnp.isclose(p[0], vmax[0])
           elif func == 'front':   
                func = lambda p  : jnp.isclose(p[1],  vmax[1])
           elif func == 'back':   
                func = lambda p  : jnp.isclose(p[1], vmin[1])
           elif func == 'bottom':   
                func = lambda p  : jnp.isclose(p[2], vmin[2])
           elif func == 'top':   
                func = lambda p  : jnp.isclose(p[2], vmax[2])
           elif func == 'everywhere':   
                return jnp.arange(len(self.boundary_centroids))
        
        
        #return jax.vmap(func)(self.boundary_centroids).nonzero()[0]
        return func(self.boundary_centroids.T).nonzero()[0]
      
          
    
    def compute_function_on_centroids(self,func):
       """Select specific regions""" 

       out = jax.vmap(func)(self.centroids)

       return jax.tree.map(
        lambda x: x.reshape(self.grid, order="F") if isinstance(x, jnp.ndarray) else x,
       out
       )
    
    def select_internal_boundary(self,func):
       """Get select boundaries""" 

       return func(self.face_centroids.T).nonzero()[0]


    def cell2side(self,func):

        return partial(func,i=self.smap[:,0],j=self.smap[:,1])
    
    #@eqx.filter_jit
    def grad_interpolation(self,f):
        """Gradient of the interpolation of a given field f defined at centroids"""

        #method = 'catmull-rom'
        method = 'cubic2'
        period = [
    None if self.periodic[0] * self.size[0] == 0 else self.periodic[0] * self.size[0],
    None if self.periodic[1] * self.size[1] == 0 else self.periodic[1] * self.size[1],
    None if self.periodic[2] * self.size[2] == 0 else self.periodic[2] * self.size[2],
        ]
            
        
        interpolator = lambda p: interp3d(*p,self.x_centroids, self.y_centroids, self.z_centroids, f,method=method,period=period)

        return jax.vmap(jax.grad(interpolator))(self.centroids).reshape((*self.grid,3),order='F')
    
    #@eqx.filter_jit
    def hessian_interpolation(self,f):
        """Hessian of the interpolation of a given field f defined at centroids"""
        period = [
    None if self.periodic[0] * self.size[0] == 0 else self.periodic[0] * self.size[0],
    None if self.periodic[1] * self.size[1] == 0 else self.periodic[1] * self.size[1],
    None if self.periodic[2] * self.size[2] == 0 else self.periodic[2] * self.size[2],
        ]


        #method = 'catmull-rom'
        method = 'cubic2'
        interpolator =  lambda p: interp3d(*p,self.x_centroids, self.y_centroids, self.z_centroids, f,method=method,period=period)

        return jax.vmap(jax.hessian(interpolator))(self.centroids).reshape((*self.grid,3,3),order='F')
    
    def convolve_with_kernel(self,kernel,FFT)->Callable:
        
       
     if self.periodic[0] and not self.periodic[1] and not self.periodic[2]:
        
        # [1,0,0]
        return lambda x: jax.scipy.signal.convolve(
            jnp.pad(x, ((self.grid[0], self.grid[0]), (0, 0),(0, 0)), mode='wrap'), kernel, mode='same', method='fft'
        )[self.grid[0]:2*self.grid[0], :,:]

     elif not self.periodic[0] and self.periodic[1] and not self.periodic[2]:
        # [0,1,0]
        return lambda x: jax.scipy.signal.convolve(
            jnp.pad(x, ((0, 0), (self.grid[1], self.grid[1]),(0,0)), mode='wrap'), kernel, mode='same', method='fft'
        )[:, self.grid[1]:2*self.grid[1],:]

     elif not self.periodic[0] and not self.periodic[1] and not self.periodic[2]:
        # [0,0,0]
        
        return lambda x: jax.scipy.signal.convolve(x, kernel, mode='same', method='fft')

     elif self.periodic[0] and self.periodic[1] and self.periodic[2]:
        # [1,1,1]
        if FFT:
         kernel_shifted_FFT = jnp.fft.fftn(jnp.fft.ifftshift(kernel))
         return lambda x: jnp.real(jnp.fft.ifftn(jnp.fft.fftn(x) *  kernel_shifted_FFT))
        
        else:
         return lambda x: jax.scipy.signal.convolve(
             jnp.pad(x, ((self.grid[0], self.grid[0]), (self.grid[1], self.grid[1]),(self.grid[2],self.grid[2])), mode='wrap'), kernel, mode='same', method='fft'
         )[self.grid[0]:2*self.grid[0], self.grid[1]:2*self.grid[1],self.grid[2]:2*self.grid[2]]  

     elif not self.periodic[0] and not self.periodic[1] and self.periodic[2]:
        # [0,0,1]
        return lambda x: jax.scipy.signal.convolve(
            jnp.pad(x, ((0,0), (0, 0),(self.grid[2],self.grid[2])), mode='wrap'), y, mode='same', method='fft'
        )[:,:,self.grid[2]:2*self.grid[2]]  
     
     elif not self.periodic[0] and self.periodic[1] and self.periodic[2]:
        # [0,1,1]
        return lambda x, y: jax.scipy.signal.convolve(
            jnp.pad(x, ((0,0), (self.grid[1], self.grid[1]),(self.grid[2],self.grid[2])), mode='wrap'), y, mode='same', method='fft'
        )[:,self.grid[1]:2*self.grid[1],self.grid[2]:2*self.grid[2]]  
     
     elif  self.periodic[0] and  not self.periodic[1] and self.periodic[2]:
        # [1,0,1]
        return lambda x, y: jax.scipy.signal.convolve(
            jnp.pad(x, ((self.grid[0],self.grid[0]), (0, 0),(self.grid[2],self.grid[2])), mode='wrap'), y, mode='same', method='fft'
        )[self.grid[0]:2*self.grid[0],:,self.grid[2]:2*self.grid[2]] 
     
     elif  self.periodic[0] and  self.periodic[1] and not self.periodic[2]:
        
        # [1,1,0]
        return lambda x, y: jax.scipy.signal.convolve(
            jnp.pad(x, ((self.grid[0],self.grid[0]), (self.grid[1], self.grid[1]),(0,0)), mode='wrap'), y, mode='same', method='fft'
        )[self.grid[0]:2*self.grid[0],self.grid[1]:2*self.grid[1],:]
     
     else:
        raise NotImplementedError("This case should never happen")

