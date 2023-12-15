bl_info = {
    "name": "Simple Morph 219",
    "description": "Suitable for building repeatable meshes that each require unique simple tweaks to the same shape.",
    "author": "S.A. Lowell",
    "version": (0.2, 396624, 2023.12, 15.08, 16.26, 1702628219),
    "blender": (4, 0, 2),
    "location": "View3D > N-Panel(Side Panel) > Item > Simple Morph 219",
    "warning": "Currently in beta.",
    "doc_url": "https://salowell.com/simplemorph219",
    "tracker_url": "https://salowell.com/simplemorph219",
    "support": "COMMUNITY",
    "category": "Mesh",
}

import bpy
from bpy.props import EnumProperty
from bpy.types import Operator, Panel
from bpy.utils import register_class, unregister_class

import mathutils

from SimpleMorph219 import simplemorph219, salowell_bpy_lib

def register():
    register_class( simplemorph219.SIMPLE_MORPH_219_op )
    register_class( simplemorph219.SIMPLE_MORPH_219_PT_panel )

def unregister():
    unregister_class( simplemorph219.SIMPLE_MORPH_219_op )
    unregister_class( simplemorph219.SIMPLE_MORPH_219_PT_panel )

if __name__ == '__main__':
    register()