#TODO: Switch all mesh operations to bmesh operations. This should drastically increase the speed of these scripts.
import bpy
from bpy.props import EnumProperty
from bpy.types import Operator, Panel
from bpy.utils import register_class, unregister_class

import mathutils
from . import simplemorph219, salowell_bpy_lib, realcorner219

bl_info = {
    "name": "Simple Morph 219",
    "description": "Suitable for building repeatable meshes that each require unique simple tweaks to the same shape.",
    "author": "S.A. Lowell",
    "version": (0.16, 1600087, 2024.03, 23.16, 26.59, 1711211219.0),
    "blender": (4, 0, 2),
    "location": "View3D > N-Panel(Side Panel) > Item > Simple Morph 219",
    "warning": "Currently in beta.",
    "doc_url": "https://salowell.com/simplemorph219",
    "tracker_url": "https://salowell.com/simplemorph219",
    "support": "COMMUNITY",
    "category": "Mesh",
}

if "bpy" in locals():
    import importlib
    
    if "simplemorph219" in locals():
        importlib.reload( simplemorph219 )
    
    if "salowell_bpy_lib" in locals():
        importlib.reload( salowell_bpy_lib )
    
    if "realcorner219" in locals():
        realCorner219CurrentState = realcorner219.realCorner219CurrentState.value
        realCorner219LastUpdate = realcorner219.realCorner219LastUpdate
        realCorner219SelectedBaseObjName:str = realcorner219.realCorner219SelectedBaseObjName
        realCorner219ModifiedObjName:str = realcorner219.realCorner219ModifiedObjName
        realcorner219HandleSelectDeselectFunctionLocked:bool = realcorner219.realcorner219HandleSelectDeselectFunctionLocked
        
        importlib.reload( realcorner219 )
        
        realcorner219.realCorner219CurrentState = realcorner219.realCorner219States(realCorner219CurrentState)
        realcorner219.realCorner219LastUpdate = realCorner219LastUpdate
        realcorner219.realCorner219SelectedBaseObjName = realCorner219SelectedBaseObjName
        realcorner219.realCorner219ModifiedObjName = realCorner219ModifiedObjName
        realcorner219.realcorner219HandleSelectDeselectFunctionLocked = realcorner219HandleSelectDeselectFunctionLocked

def register():
    register_class( simplemorph219.SIMPLE_MORPH_219_op )
    register_class( simplemorph219.SIMPLE_MORPH_219_PT_panel )
    register_class( simplemorph219.SIMPLE_MORPH_219_ANGLE_CONTROLLERS_op )
    register_class( simplemorph219.SIMPLE_MORPH_219_DECOMPILE_op )
    
    realcorner219.register()

def unregister():
    unregister_class( simplemorph219.SIMPLE_MORPH_219_op )
    unregister_class( simplemorph219.SIMPLE_MORPH_219_PT_panel )
    unregister_class( simplemorph219.SIMPLE_MORPH_219_ANGLE_CONTROLLERS_op )
    unregister_class( simplemorph219.SIMPLE_MORPH_219_DECOMPILE_op )
    
    realcorner219.unregister()

if __name__ == '__main__':
    register()
