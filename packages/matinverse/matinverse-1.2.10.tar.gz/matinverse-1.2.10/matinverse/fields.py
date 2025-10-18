import equinox as eqx
import jax.numpy as jnp
from typing import Dict, Any
#from matinverse.geometry2D import Geometry2D
#from matinverse.geometry3D import Geometry3D
#from matinverse.IO import WriteVTR
import equinox as eqx
import jax.numpy as jnp
from typing import Dict, Any
import math

class Fields(eqx.Module):

    # required fields first
    field_dict: Dict[str, dict] = eqx.field(default_factory=dict)

    # static metadata fields can have defaults
    meta_dict: Dict[str, Dict[str, Any]] = eqx.field(static=True, default_factory=dict)


    def add_field(self, name, data, surface=False, units="ad", 
                  batch_map=None, time_stamps=None):
        
        
        new_field_dict = dict(self.field_dict)
        new_field_dict[name] = {'data':data,'time_stamps':time_stamps}
        new_meta_dict = dict(self.meta_dict)
        new_meta_dict[name] = {
            "surface": surface, 
            "units": units,                # safe: static
            "batch_map": batch_map, 
        }

        return Fields(field_dict=new_field_dict, meta_dict=new_meta_dict)

    def __getitem__(self, key):
            if key not in self.field_dict:
                raise KeyError(f"No field with name '{key}'")
            data = self.field_dict[key]['data']

            if self.field_dict[key]['time_stamps'] is None:
                return data

            batch_map = self.meta_dict[key]['batch_map']
            batch_size =  math.prod(batch_map)

            if len(self.field_dict[key]['time_stamps']) == 1 and batch_size > 1:

                idx = (slice(None),) * len(batch_map) + (0,)

                return data[idx]

            if len(self.field_dict[key]['time_stamps']) == 1 and batch_size == 1:
                return data[0,0]
            
         
            return data

