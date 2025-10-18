import math
import numpy as np
import xml.etree.ElementTree as ET
from .fields import Fields


def WriteVTR(  geo,
               fields: Fields,
               filename="output"):

    dim = geo.dim
   
    vtkfile = ET.Element("VTKFile",
                         type="RectilinearGrid",
                         version="0.1",
                         byte_order="LittleEndian")

    nx, ny = geo.grid[0]+1, geo.grid[1]+1
    if dim == 2:
     nz = 1
     node_z = np.array([0.0])
    else:
     nz = geo.grid[2]+1
     node_z = geo.z_nodes

    
    grid = ET.SubElement(vtkfile, "RectilinearGrid",
                         WholeExtent=f"0 {nx-1} 0 {ny-1} 0 {nz-1}")
    piece = ET.SubElement(grid, "Piece",
                          Extent=f"0 {nx-1} 0 {ny-1} 0 {nz-1}")

    # Coordinates
    coords = ET.SubElement(piece, "Coordinates")
    for name, arr in zip(["X","Y","Z"], [geo.x_nodes,geo.y_nodes,node_z]):
        da = ET.SubElement(coords, "DataArray",
                           type="Float32", Name=name,
                           NumberOfComponents="1", format="ascii")
       
        da.text = ' '.join(map(str, arr))

    # Always create CellData container
    celldata = ET.SubElement(piece, "CellData")

    # Variables
    metadata = fields.meta_dict
    for variable_name in fields.field_dict.keys():
        meta = metadata[variable_name]
        if meta['surface']:
            continue

        data = fields[variable_name]
        
        batch_map = meta['batch_map']

        #Augment for convenience (TODO: this could be done better)
        if batch_map is None or math.prod(batch_map) == 1 :
            batch_map = (1,)
            data = data[None,...]
        
        I = np.array(np.unravel_index(np.arange(np.prod(batch_map)), batch_map)).T
       
        for batch in I:
           
            if math.prod(batch_map) == 1:
                name =  f"{variable_name}_[{meta['units']}]"
            else:    
                
                name = f"{variable_name}_" + '_'.join(map(str, batch)) + f"_[{meta['units']}]"

            arr = np.array(data)[tuple(batch)]

            if arr.ndim == dim:
                da = ET.SubElement(celldata, "DataArray",
                                   type="Float32", Name=name,
                                   NumberOfComponents="1", format="ascii")
                
                da.text = ' '.join(map(str, arr.flatten(order="F")))

            #Vector field
            elif arr.ndim == dim+1:
                
                da = ET.SubElement(celldata, "DataArray",
                                   type="Float32", Name=name,
                                   NumberOfComponents=str(dim), format="ascii")

                lines = [' '.join(map(str, row)) for row in arr.reshape((-1, dim), order="F")]
                da.text = '\n'.join(lines)

            #Tensor field
            elif arr.ndim == dim+2:
                da = ET.SubElement(celldata, "DataArray",
                                   type="Float32", Name=name,
                                   NumberOfComponents=str(dim*dim), format="ascii")
                
                lines = [' '.join(map(str, row.flatten())) for row in arr.reshape((-1, dim*dim), order="F")]
                da.text = '\n'.join(lines)

            else:
            
                raise ValueError(f"Unsupported shape for {name}: {arr.shape}")

    # Write file
    ET.ElementTree(vtkfile).write(filename + ".vtr", encoding="utf-8", xml_declaration=True)
   

    



