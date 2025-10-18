import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from numpy.ma import masked_array
from jax import numpy as jnp
import numpy as np
import matplotlib.patches as patches
import plotly.io as pio
pio.renderers.default = "notebook_connected"
import plotly.graph_objects as go


def cube_mesh(ix, iy, iz, x_coords, y_coords, z_coords):
    # voxel bounds
    x0, x1 = x_coords[ix],   x_coords[ix+1]
    y0, y1 = y_coords[iy],   y_coords[iy+1]
    z0, z1 = z_coords[iz],   z_coords[iz+1]

    # 8 cube vertices
    vertices = np.array([
        [x0, y0, z0], [x1, y0, z0],
        [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1],
        [x1, y1, z1], [x0, y1, z1]
    ])

    # faces (triangles, two per side)
    faces = np.array([
        [0, 1, 2], [0, 2, 3],  # bottom
        [4, 5, 6], [4, 6, 7],  # top
        [0, 1, 5], [0, 5, 4],  # front
        [1, 2, 6], [1, 6, 5],  # right
        [2, 3, 7], [2, 7, 6],  # back
        [3, 0, 4], [3, 4, 7],  # left
    ])

    return vertices, faces


def plot3D(geo, data, write=False):
    x_coords = geo.x_nodes
    y_coords = geo.y_nodes
    z_coords = geo.z_nodes
    voxels = np.where(data > 0.5, 1, 0)
    filled = np.argwhere(voxels)

    all_vertices, all_faces, all_colors = [], [], []
    offset = 0

    for (ix, iy, iz) in filled:
        verts, faces = cube_mesh(ix, iy, iz, x_coords, y_coords, z_coords)
        all_vertices.append(verts)
        all_faces.append(faces + offset)

        # repeat cube's value for its 8 vertices
        val = float(data[ix, iy, iz])
        all_colors.extend([val] * verts.shape[0])

        offset += verts.shape[0]

    if not all_vertices:  # nothing to draw
        return

    all_vertices = np.concatenate(all_vertices, axis=0)
    all_faces = np.concatenate(all_faces, axis=0)
    all_colors = np.array(all_colors)

    # Extract Mesh3d inputs
    X, Y, Z = all_vertices.T
    I, J, K = all_faces.T

    mesh = go.Mesh3d(
        x=X, y=Y, z=Z,
        i=I, j=J, k=K,
        intensity=all_colors,             # per-vertex values
        colorscale="Viridis",             # choose any colorscale
        cmin=float(data.min()),
        cmax=float(data.max()),
        flatshading=True,
        opacity=1,
        showscale=True                    # show colorbar
    )

    fig = go.Figure(data=[mesh])

    dx = float(x_coords[-1] - x_coords[0])
    dy = float(y_coords[-1] - y_coords[0])
    dz = float(z_coords[-1] - z_coords[0])
    m = max(dx, dy, dz)

    fig.update_layout(
        scene=dict(
            aspectmode='manual',
            aspectratio=dict(x=dx/m, y=dy/m, z=dz/m),
            xaxis=dict(visible=True),
            yaxis=dict(visible=True),
            zaxis=dict(visible=True),
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    if write:
        fig.write_html('voxels.html', config={'displayModeBar': False})

    fig.show()


def plot2D(data,geo,**argv):
    """Plot Masked data"""


    data = jnp.zeros((geo.N)).at[geo.local2global].set(data.flatten()).reshape(geo.grid)


    #Design mask
    design_mask = argv.setdefault('design_mask', jnp.ones_like(geo.mask)).reshape(geo.grid)
    design_mask = jnp.where(design_mask>0.5,1,0)


    #Mask for excluding part of the domain from the simulation
    mask = np.logical_and(geo.mask,design_mask)


    Lx,Ly = geo.size

    N = data.shape[0]
    kx = 1
    ky = 1
    Px = 0
    Py = 0
    if geo.periodic[0]:
        kx = 3
        Px = N #Because it is extended
        Lx *=3
    if geo.periodic[1]:
        ky = 3
        Py = N #Because it is extended
        Ly *=3

    if not 'axis' in argv.keys():
       ax = plt.gca()
    else:
       ax = argv['axis']



    #plot the unit cell
    if geo.periodic[0] and geo.periodic[1]:
       ax.plot([-geo.size[0]/2,-geo.size[0]/2,geo.size[0]/2,geo.size[0]/2,-geo.size[0]/2],[-geo.size[1]/2,geo.size[1]/2,geo.size[1]/2,-geo.size[1]/2,-geo.size[1]/2],'r--',linewidth=2)


    data = np.pad(data,(Px,Py),'wrap')


    mask = np.pad(np.logical_not(mask),(Px,Py),'wrap')


    data = masked_array(data, mask=mask)


    extent= [-geo.size[0]/2*kx,geo.size[0]/2*kx,-geo.size[1]/2*ky,geo.size[1]/2*ky]

    cmap = argv.setdefault('cmap','viridis')


    vmin = argv.setdefault('vmin',data.min())
    vmax = argv.setdefault('vmax',data.max())
    img = ax.imshow(data,extent = extent,cmap=cmap,aspect='equal',vmin=vmin,vmax=vmax)


    #Plot contours
    DX = geo.size[0]/geo.grid[0]
    DY = geo.size[1]/geo.grid[1]
    for contour in argv.setdefault('contours',[]):


        contour = jnp.where(contour>0.5,1,0)

        I1 = jnp.logical_xor(contour.flatten()[geo.smap[:,0]],contour.flatten()[geo.smap[:,1]])
        I1 = jnp.where(I1)[0]
        I_vertical = I1[jnp.where(I1  < len(geo.face_centroids)//2)[0]]
        I_horizontal = I1[jnp.where(I1  >= len(geo.face_centroids)//2)[0]]

        PP = [[0,0]]
        if geo.periodic[0]:
              PP.append([geo.size[0],0])
              PP.append([-geo.size[0],0])
        if geo.periodic[1]:
              PP.append([0,geo.size[1]])
              PP.append([0,-geo.size[1]])
        if geo.periodic[0] and geo.periodic[1]:
              PP.append([geo.size[0],geo.size[1]])
              PP.append([-geo.size[0],-geo.size[1]])
              PP.append([geo.size[0],-geo.size[1]])
              PP.append([-geo.size[0],geo.size[1]])

        for P in PP:


         for a in I_vertical:
           c = geo.face_centroids[a]
           ax.plot([c[0]+P[0],c[0]+P[0]],[c[1]-DY/2+P[1],c[1] + DY/2+P[1]],'r',lw=1,zorder=4)

         for a in I_horizontal:
           c = geo.face_centroids[a]
           ax.plot([c[0]-DX/2+P[0],c[0] + DX/2+P[0]],[c[1]+P[1],c[1]+P[1]],'r',lw=1,zorder=4)


    

    #Line contours
    line_contours = argv.setdefault('line_contours',[])
    if len(line_contours) > 0:
        ax.contour(np.flipud(data), extent=extent, levels=line_contours, colors='white')

    #Flux lines #This does not work with PBCs yet
    flux_lines = argv.setdefault('flux_lines',[])
    if len(flux_lines) > 0:
        xc = np.linspace(-Lx / 2, Lx / 2, N)
        yc = np.linspace(-Ly / 2, Ly / 2, N)
        ax.streamplot(xc, yc, jnp.flipud(flux_lines[:, 0].reshape(geo.grid).T), jnp.flipud(flux_lines[:, 1].reshape(geo.grid).T), color='w')

    #Add a border
    if argv.setdefault('border',False):

     rect = patches.Rectangle(
      (-Lx/2, -Ly/2), Lx, Ly,
      linewidth=2, edgecolor='red', facecolor='none')

     ax.add_patch(rect)

    ax.axis('off')
    ax.set_aspect('equal')
    ax.set_xlim([-Lx/2,Lx/2])
    ax.set_ylim([-Ly/2,Ly/2])
    if argv.setdefault('colorbar',False):
     cbar = plt.colorbar(img)
     cbar.set_label(argv['colorbar_title'], fontsize=12)

    if argv.setdefault('write',False):
        plt.savefig('data.png', dpi=argv.setdefault('dpi',100),bbox_inches='tight', pad_inches=0)

    if not 'axis' in argv.keys():
     plt.tight_layout()
     plt.ioff()
     plt.show()

    return img

def movie2D(data, geo, **argv):


    NT = len(data) #NT is the optimization iteration, not the time step

    data = jnp.zeros((NT,geo.N)).at[:,geo.local2global].set(data).reshape(((NT,) + tuple(geo.grid))) 
    

  
    NT, grid, grid = data.shape

    #Init design mask

    mask = geo.mask
    #-------


    fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor((1, 1, 1, 0))
    ax.axis('off')

     #plot the unit cell
    if geo.periodic[0] and geo.periodic[1]:
       unit_cell, = ax.plot([-geo.size[0]/2,-geo.size[0]/2,geo.size[0]/2,geo.size[0]/2,-geo.size[0]/2],[-geo.size[1]/2,geo.size[1]/2,geo.size[1]/2,-geo.size[1]/2,-geo.size[1]/2],'r--',linewidth=2)
    else:
         unit_cell, = ax.plot([], [], 'r--', linewidth=0)

    vmax = data.max()

    kx = 1
    ky = 1
    Px = 1
    Py = 1
    if geo.periodic[0]:
        kx = 3
        Px = grid
    if geo.periodic[1]:
        ky = 3
        Py = grid

    data = np.pad(data, ((0, 0), (Px, Px), (Py, Py)), mode='wrap')
    mask = np.pad(mask, ((Px, Px), (Py, Py)), mode='wrap')

    cmap = argv.setdefault('cmap', 'viridis')

   

    cax = ax.imshow(
        data[0, :, :], cmap=cmap, 
        extent=[-geo.size[0] / 2 * kx, geo.size[0] / 2 * kx, 
                -geo.size[1] / 2 * ky, geo.size[1] / 2 * ky]
    )
    cax.set_clim(0, data[0, :, :].max())
    ax.set_xlim([-geo.size[0] / 2 * kx, geo.size[0] / 2 * kx])
    ax.set_ylim([-geo.size[1] / 2 * ky, geo.size[1] / 2 * ky])


  

    def update(frame):
     
     cax.set_data(data[frame, :, :])  # Transpose data for correct orientation

     return cax,unit_cell




    # Creating the animation
    ani = FuncAnimation(fig, update, frames=NT, blit=True, interval=0.5, repeat=False)

   
    filename = argv.setdefault('filename', 'animation.gif')
    ani.save(filename, writer=PillowWriter(fps=200), 
         savefig_kwargs={'transparent': True, 'pad_inches': 0})
    
    if argv.setdefault('show',True):
     plt.ioff()
     plt.tight_layout()
     plt.show()


