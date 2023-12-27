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
    "version": (0.10, 427330, 2023.12, 27.13, 36.59, 1703684219),
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

def register():
    register_class( simplemorph219.SIMPLE_MORPH_219_op )
    register_class( simplemorph219.SIMPLE_MORPH_219_PT_panel )
    register_class( simplemorph219.SIMPLE_MORPH_219_ANGLE_CONTROLLERS_op )
    register_class( simplemorph219.SIMPLE_MORPH_219_DECOMPILE_op )

def unregister():
    unregister_class( simplemorph219.SIMPLE_MORPH_219_op )
    unregister_class( simplemorph219.SIMPLE_MORPH_219_PT_panel )
    unregister_class( simplemorph219.SIMPLE_MORPH_219_ANGLE_CONTROLLERS_op )
    unregister_class( simplemorph219.SIMPLE_MORPH_219_DECOMPILE_op )

if __name__ == '__main__':
    register()
