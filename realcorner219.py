from ctypes import Array

from enum import Enum

import bpy

from bpy.types import Menu, Operator, Panel
from bpy.props import ( BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty )
from bpy.utils import register_class, unregister_class

import bmesh
import mathutils

from . import salowell_bpy_lib, simplemorph219

#[0] = 1 -> vertex
#[0] = 2 -> edge
#[0] = 3 -> face
#[1] = Index of the selected vertex/edge/face within the current object/mesh
#[2] = The layer_maps object which contains every layer_map leading up to the currently selected layer.
pie_menu_selection_data:Array = [0, 0, None]

class realcorner219_procedural_edge_select_types( Enum ):
    EDGE = 0
    LEFT_EDGE = 1
    EDGE_RIGHT = 2
    LEFT_EDGE_RIGHT = 3
    LEFT_RIGHT = 4
    LEFT = 5
    RIGHT = 6
    BEVEL_EDGE = 7
    BEVEL_LEFT_EDGE = 8
    BEVEL_EDGE_RIGHT = 9
    BEVEL_LEFT_EDGE_RIGHT = 10
    BEVEL_LEFT_RIGHT = 11
    BEVEL_LEFT = 12
    BEVEL_RIGHT = 13

class realcorner219_procedural_beveled_edge_select_types( Enum ):
    TOP = 0
    TOP_MIDDLE = 1
    MIDDLE = 2
    MIDDLE_BOTTOM = 3
    BOTTOM = 4
    PERCENT = 5

simple_morph_219_object_list:Array = []

realCorner219PropName = 'realCorner219_'

class edge_select_pie_menu(Menu):
    bl_idname = 'edge_select_pie_menu'
    bl_label = 'Edge Options'
    
    def execute( self, context ):
        return {'FINISHED'}
    
    def draw(self, context):
        global pie_menu_selection_data
        
        layer_index:int = salowell_bpy_lib.get_selected_layer_index() - 1
        layer_name:str = 'realCorner219_' + str(layer_index)
        
        layout = self.layout
        pie = layout.menu_pie()
        
        if pie_menu_selection_data[0] == 1:
            vertex_relative_map:dict = pie_menu_selection_data[2].layer_maps[layer_name].get_bevel_vertex_relative_map(pie_menu_selection_data[1])
            
            if len(vertex_relative_map['beveled_vertices_to_last_vertex']) != 0:
                edge_operator = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last Vertex <- Vertex', icon = 'EVENT_A')
                edge_operator.action = 'BEVEL_-_LAST_VERTEX_-_VERTEX'
            
            left_vertex_menu:bool = False
            right_vertex_menu:bool = False
            if len(vertex_relative_map['beveled_leftright_vertices_to_last_edge']) != 0:
                for beveled_leftright_vertices_to_last_edge in vertex_relative_map['beveled_leftright_vertices_to_last_edge']:
                    
                    if beveled_leftright_vertices_to_last_edge[1] == 0:
                        left_vertex_menu = True
                    else:
                        right_vertex_menu = True
            
            if left_vertex_menu:
                edge = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last Edge <- Left Vertex', icon = 'EVENT_A')
                edge.action = 'BEVEL_-_LAST_EDGE_-_LEFT_VERTEX'
            
            if right_vertex_menu:
                edge = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last Edge <- Right Vertex', icon = 'EVENT_A')
                edge.action = 'BEVEL_-_LAST_EDGE_-_RIGHT_VERTEX'
            
            if vertex_relative_map['unbeveled_vertices'] >= 0:
                edge = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last Vertex <- Current Vertex', icon = 'EVENT_A')
                edge.action = 'BEVEL_-_LAST_VERTEX_-_CURRENT_VERTEX'
        if pie_menu_selection_data[0] == 2:
            edge_relative_map:dict = pie_menu_selection_data[2].layer_maps[layer_name].get_bevel_edge_relative_map(pie_menu_selection_data[1])
            
            if len(edge_relative_map['beveled_edges_to_last_vertex']) != 0:
                edge_operator = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last Vertex <- Edge', icon = 'EVENT_A')
                edge_operator.action = 'BEVEL_-_LAST_VERTEX_-_EDGE'
            
            left_edge_menu:bool = False
            right_edge_menu:bool = False
            if len(edge_relative_map['beveled_leftright_edges_to_last_edge']) != 0:
                for beveled_leftright_edges_to_last_edge in edge_relative_map['beveled_leftright_edges_to_last_edge']:
                    
                    if beveled_leftright_edges_to_last_edge[1] == 0:
                        left_edge_menu = True
                    else:
                        right_edge_menu = True
            
            if left_edge_menu:
                edge = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last Edge <- Left Edge', icon = 'EVENT_A')
                edge.action = 'BEVEL_-_LAST_EDGE_-_LEFT_EDGE'
            
            if right_edge_menu:
                edge = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last Edge <- Right Edge', icon = 'EVENT_A')
                edge.action = 'BEVEL_-_LAST_EDGE_-_RIGHT_EDGE'
            
            if len(edge_relative_map['beveled_parallel_edges_to_last_edge']) != 0:
                edge = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last Edge <- Parallel Edge', icon = 'EVENT_A')
                edge.action = 'BEVEL_-_LAST_EDGE_-_PARALLEL_EDGE'
            
            start_edge_menu:bool = False
            end_edge_menu:bool = False
            if len(edge_relative_map['beveled_startend_edges_to_last_edge']) != 0:
                for beveled_startend_edges_to_last_edge in edge_relative_map['beveled_startend_edges_to_last_edge']:
                    if edge_relative_map['beveled_startend_edges_to_last_edge'][1] == 0:
                        start_edge_menu = True
                    else:
                        end_edge_menu = True
            if start_edge_menu:
                edge = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last Edge <- Start Edge', icon = 'EVENT_A')
                edge.action = 'BEVEL_-_LAST_EDGE_-_START_EDGE'
            
            if end_edge_menu:
                edge = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last Edge <- End Edge', icon = 'EVENT_A')
                edge.action = 'BEVEL_-_LAST_EDGE_-_END_EDGE'
            
            if edge_relative_map['unbeveled_edges'] >= 0:
                edge = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last Edge <- Current Edge', icon = 'EVENT_A')
                edge.action = 'BEVEL_-_LAST_EDGE_-_CURRENT_EDGE'
        if pie_menu_selection_data[0] == 3:
            face_relative_map:dict = pie_menu_selection_data[2].layer_maps[layer_name].get_bevel_face_relative_map(pie_menu_selection_data[1])
             
            if len(face_relative_map['beveled_faces_to_last_vertex']) != 0:
                edge_operator = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last Vertex <- FACE', icon = 'EVENT_A')
                edge_operator.action = 'BEVEL_-_LAST_VERTEX_-_FACE'

            if len(face_relative_map['beveled_faces_to_last_edge']) != 0:
                edge = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last Edge <- FACES', icon = 'EVENT_A')
                edge.action = 'BEVEL_-_LAST_EDGE_-_FACES'
            
            if face_relative_map['unbeveled_faces'] >= 0:
                edge = pie.operator('view3d.handle_dynamic_edge_select', text = 'Bevel: Last FACE <- Current FACE', icon = 'EVENT_A')
                edge.action = 'BEVEL_-_LAST_FACE_-_CURRENT_FACE'

class OT_real_corner_219_handle_dynamic_edge_select( Operator ):
    bl_idname = 'view3d.handle_dynamic_edge_select'
    bl_label = 'Select Dynamic Edge'
    bl_description = 'Selecting dynamically generated edges.'
    
    action: EnumProperty(
        items = [
            ( "BEVEL_-_LAST_VERTEX_-_VERTEX", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "BEVEL_-_LAST_EDGE_-_LEFT_VERTEX", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "BEVEL_-_LAST_EDGE_-_RIGHT_VERTEX", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "BEVEL_-_LAST_VERTEX_-_CURRENT_VERTEX", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "BEVEL_-_LAST_VERTEX_-_EDGE", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "BEVEL_-_LAST_EDGE_-_LEFT_EDGE", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "BEVEL_-_LAST_EDGE_-_RIGHT_EDGE", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "BEVEL_-_LAST_EDGE_-_PARALLEL_EDGE", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "BEVEL_-_LAST_EDGE_-_START_EDGE", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "BEVEL_-_LAST_EDGE_-_END_EDGE", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "BEVEL_-_LAST_EDGE_-_CURRENT_EDGE", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "BEVEL_-_LAST_VERTEX_-_FACE", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "BEVEL_-_LAST_EDGE_-_FACES", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "BEVEL_-_LAST_FACE_-_CURRENT_FACE", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
        ]
    )
    
    def execute( self, context ):
        global realCorner219LastUpdate, realCorner219SelectedBaseObjName, realCorner219ModifiedObjName
        
        selected_edges = salowell_bpy_lib.get_selected_edges(bpy.context.selected_objects[0])[1]
        
        edge_id:int = -1
        
        if len(selected_edges) > 0:
            edge_id = selected_edges[0]
        
        s_m_219_object:simple_morph_219_object = create_if_not_exists_simple_morph_219_object(realCorner219SelectedBaseObjName)
        previous_layer_key = get_previous_real_corner_custom_prop_key(bpy.context.selected_objects[0], context.scene.realCorner219Layers)
        
        selection_value_tmp = edge_to_edge_reference_bevel(edge_id, s_m_219_object.layer_maps, bpy.data.objects[s_m_219_object.object_name], previous_layer_key )
        selection_value_tmp2 = selection_value_tmp
        selection_value_tmp = []
        previous_layer_index:int = int(previous_layer_key.split('_')[1])
        
        for value in selection_value_tmp2:
            if value[3] == previous_layer_index:
                selection_value_tmp.append(value)
        
        selection_value:Array = []
        
        layer_properties:dict = realCornerPropIndexToDict(bpy.context.selected_objects[0], context.scene.realCorner219Layers)
        
        if self.action == 'BEVEL_-_LAST_EDGE_-_CURRENT_EDGE':
            for value in selection_value_tmp:
                if value[0] == 0:
                    value = get_low_dynamic_edge_from_dynamic_edge(value, s_m_219_object.layer_maps, bpy.data.objects[s_m_219_object.object_name])
                    selection_value.append(value)
        elif self.action == 'BEVEL_-_LAST_EDGE_-_START_EDGE':
            for value in selection_value_tmp:
                if value[0] == 1:
                    value = get_low_dynamic_edge_from_dynamic_edge(value, s_m_219_object.layer_maps, bpy.data.objects[s_m_219_object.object_name])
                    selection_value.append(value)
        elif self.action == 'BEVEL_-_LAST_EDGE_-_END_EDGE':
            for value in selection_value_tmp:
                if value[0] == 2:
                    value = get_low_dynamic_edge_from_dynamic_edge(value, s_m_219_object.layer_maps, bpy.data.objects[s_m_219_object.object_name])
                    selection_value.append(value)
        elif self.action == 'BEVEL_-_LAST_EDGE_-_PARALLEL_EDGE':
            for value in selection_value_tmp:
                if value[0] == 3:
                    value = get_low_dynamic_edge_from_dynamic_edge(value, s_m_219_object.layer_maps, bpy.data.objects[s_m_219_object.object_name])
                    selection_value.append(value)
        elif self.action == 'BEVEL_-_LAST_EDGE_-_LEFT_EDGE':
            for value in selection_value_tmp:
                if value[0] == 4:
                    value = get_low_dynamic_edge_from_dynamic_edge(value, s_m_219_object.layer_maps, bpy.data.objects[s_m_219_object.object_name])
                    selection_value.append(value)
        elif self.action == 'BEVEL_-_LAST_EDGE_-_RIGHT_EDGE':
            for value in selection_value_tmp:
                if value[0] == 5:
                    value = get_low_dynamic_edge_from_dynamic_edge(value, s_m_219_object.layer_maps, bpy.data.objects[s_m_219_object.object_name])
                    selection_value.append(value)
        else:
            selection_value = selection_value_tmp
        
        already_added:Array = [False] * len(selection_value)
        
        for index in range(len(selection_value)):
            for edge_reference in layer_properties['edge_references']:
                if salowell_bpy_lib.arrays_equal(edge_reference, selection_value[index]):
                    already_added[index] = True
                    break
        
        for index in range(len(already_added)):
            if not already_added[index]:
                layer_properties['edge_references'].append(selection_value[index])
            index += 1
        
        layer_properties['edges'] = []
        
        real_corner_prop_string:str = realCornerPropDictToStringBevel( layer_properties )
        bpy.data.objects[realCorner219SelectedBaseObjName][ context.scene.realCorner219Layers ] = real_corner_prop_string
        bpy.data.objects[realCorner219ModifiedObjName][ context.scene.realCorner219Layers ] = real_corner_prop_string
          
        return {'FINISHED'}

class simple_morph_219_layer_map():
    """
    A comprehensive map of a single layer in a Simple Morph 219 object
    """
    blender_mesh:bmesh.types.BMesh = None#The bmesh for this layer
    previous_blender_mesh:bmesh.types.BMesh = None
    previous_selected_edges:Array = []#Array of the edges that were selected to perform the bevel which created this new blender_mesh
    new_face_ids:Array = []
    
    beveled_vertices_to_original_edge:dict = {}#The newely beveled vertices mapped back to the original layer edge
    beveled_vertices_to_last_edge:dict = {}#The newely beveled vertices mapped back to the last edge.
    beveled_vertices_to_last_vertex:dict = {}#The newely beveled vertices mapped back to the last vertex.
    
    beveled_leftright_vertices_to_last_edge:dict = {}
    beveled_leftright_vertices_to_original_edge:dict = {}

    beveled_terminating_vertices_to_last_edge:dict = {}
    beveled_terminating_vertices_to_original_edge:dict = {}
    
    beveled_edges_to_original_edge:dict = {}
    beveled_edges_to_last_edge:dict = {}
    beveled_edges_to_last_vertex:dict = {}
    
    beveled_leftright_edges_to_last_edge:dict = {}#Edges formed between two beveled corners.
    beveled_leftright_edges_to_original_edge:dict = {}#Edges formed between two beveled corners.
    
    beveled_terminating_edges_to_last_edge:dict = {}#Edges at the end of a bevel, beyond wich there are no connecting bevels.
    beveled_terminating_edges_to_original_edge:dict = {}#Edges at the end of a bevel, beyond wich there are no connecting bevels.
    
    beveled_parallel_edges_to_last_edge:dict = {}#Edges formed parallel along a bevel
    beveled_parallel_edges_to_original_edge:dict = {}#Edges formed parallel along a bevel
    
    beveled_startend_edges_to_original_edge:dict = {} #The edges that define the start and end of a bevel
    beveled_startend_edges_to_last_edge:dict = {} #The edges that define the start and end of a bevel
    
    beveled_leftright_edges_to_last_extend_edge:dict = {}#Edges formed between two beveled edges linked to the previous edge they extend.
    
    beveled_faces_to_original_edge:dict = {}#The newely beveled faces mapped to the original layer edge.
    beveled_faces_to_last_edge:dict = {}#The newely beveled faces mapped to the previous layer edge.
    beveled_faces_to_last_vertex:dict = {}
    
    beveled_terminating_faces_to_original_vertex:dict = {}
    beveled_terminating_faces_to_last_vertex:dict = {}
    
    unbeveled_vertices:dict = {}#The unbeveled vertices mapped back to their previous IDs
    unbeveled_edges:dict = {}#The unbeveled edges mapped back to their previous IDs
    unbeveled_faces:dict = {}#The unbeveled faces mapped back to their previous IDs
    
    def edge_is_startend_edge(self, edge_id) -> bool:
        for previous_edge_id in self.beveled_startend_edges_to_last_edge:
            if edge_id in self.beveled_startend_edges_to_last_edge[previous_edge_id]:
                return True
        
        return False
    
    def get_bevel_vertex_relative_map(self, vertex_id:int = 0) -> dict:
        """
        Returns every instance where the input vertex_id found on blender_mesh maps back to previous_blender_mesh
        
        Parameters
        ----------
        vertex_id: int
            The vertex index found within blender_mesh
        
        Returns
        -------
            A dictionary of vertex_id from blender_mesh relatively mapped back to previous_blender_mesh.
            [
                beveled_vertices_to_last_vertex:Array - Empty if not found, or a 2D array
                    [
                        0:
                            index of last vertex key,
                        1:
                            index of vertex_id
                    ],
                beveled_leftright_vertices_to_last_edge:Array - Empty if not found, or an array of 2D arrays
                    [
                        0:
                            [
                                index of last edge key,
                                0 if left, 1 if right
                            ],
                        ...
                            [
                                index of last edge key,
                                0 if left, 1 if right
                            ],
                        n:
                            [
                                index of last edge key,
                                0 if left, 1 if right
                            ],
                    ],
                unbeveled_vertices:int
                    -1 if not found, or greater than or equal to zero if found, of which this value represents the index of the last vertex key.
            ]
        """
        relative_map:dict = {
            'beveled_vertices_to_last_vertex': [],
            'beveled_leftright_vertices_to_last_edge': [],
            'unbeveled_vertices': -1,
        }
        
        found:bool = False
        keys:Array = list(self.beveled_vertices_to_last_vertex.keys())
        
        for previous_vertex_id, value in self.beveled_vertices_to_last_vertex.items():
            for current_vertex_id in value:
                if current_vertex_id == vertex_id:
                    relative_map['beveled_vertices_to_last_vertex'] = [keys.index(previous_vertex_id), value.index(current_vertex_id)]
                    found = True
                    break
            
            if found:
                break
        
        keys = list(self.beveled_leftright_vertices_to_last_edge.keys())
        
        for previous_edge_id, value in self.beveled_leftright_vertices_to_last_edge.items():
            left_vertices:Array = self.beveled_leftright_vertices_to_last_edge[previous_edge_id][0]
            right_vertices:Array = self.beveled_leftright_vertices_to_last_edge[previous_edge_id][1]
            
            if vertex_id in left_vertices:
                relative_map['beveled_leftright_vertices_to_last_edge'].append([keys.index(previous_edge_id), 0])
            
            if vertex_id in right_vertices:
                relative_map['beveled_leftright_vertices_to_last_edge'].append([keys.index(previous_edge_id), 1])
        
        keys = list(self.unbeveled_vertices.keys())
        
        for previous_vertex_id, value in self.unbeveled_vertices.items():
            current_vertex_id:int = value
            
            if current_vertex_id == vertex_id:
                relative_map['unbeveled_vertices'] = keys.index(previous_vertex_id)
                break
        
        return relative_map
    
    def get_bevel_edge_relative_map(self, edge_id:int = 0) -> dict:
        """
        Returns every instance where the input edge_id found on blender_mesh maps back to previous_blender_mesh
        
        Parameters
        ----------
        edge_id: int
            The edge index found within blender_mesh
        
        Returns
        -------
            A dictionary of edge_id from blender_mesh relatively mapped back to previous_blender_mesh.
            [
                beveled_edges_to_last_vertex:Array - Empty if not found, or a 2D array
                    [
                        0:
                            index of last vertex key,
                        1:
                            index of edge_id
                    ],
                beveled_leftright_edges_to_last_edge:Array - Empty if not found, or an array of 2D arrays
                    [
                        0:
                            [
                                index of last edge key,
                                0 if left, 1 if right
                            ],
                        ...
                            [
                                index of last edge key,
                                0 if left, 1 if right
                            ],
                        n:
                            [
                                index of last edge key,
                                0 if left, 1 if right
                            ],
                    ],
                beveled_parallel_edges_to_last_edge:Array - Empty if not found, or a 2D array
                    [
                        0:
                            index of last edge key,
                        1:
                            index of edge_id
                    ],
                beveled_startend_edges_to_last_edge:Array - Empty if not found, or a 2D array
                    [
                        0:
                            index of last edge key,
                        1:
                            0 if start, 1 if end
                    ],
                unbeveled_edges:int
                    -1 if not found, or greater than or equal to zero if found, of which this value represents the index of the last edge key.
            ]
        """
        relative_map:dict = {
            'beveled_edges_to_last_vertex': [],
            'beveled_leftright_edges_to_last_edge': [],
            'beveled_parallel_edges_to_last_edge': [],
            'beveled_startend_edges_to_last_edge': [],
            'unbeveled_edges': -1,
        }
        
        found:bool = False
        keys:Array = list(self.beveled_edges_to_last_vertex.keys())
        
        for previous_vertex_id, value in self.beveled_edges_to_last_vertex.items():
            for current_edge_id in value:
                if current_edge_id == edge_id:
                    relative_map['beveled_edges_to_last_vertex'] = [keys.index(previous_vertex_id), value.index(current_edge_id)]
                    found = True
                    break
            
            if found:
                break
        
        keys = list(self.beveled_leftright_edges_to_last_edge.keys())
        
        for previous_edge_id, value in self.beveled_leftright_edges_to_last_edge.items():
            left_edges:Array = self.beveled_leftright_edges_to_last_edge[previous_edge_id][0]
            right_edges:Array = self.beveled_leftright_edges_to_last_edge[previous_edge_id][1]
            
            if edge_id in left_edges:
                relative_map['beveled_leftright_edges_to_last_edge'].append([keys.index(previous_edge_id), 0])
            
            if edge_id in right_edges:
                relative_map['beveled_leftright_edges_to_last_edge'].append([keys.index(previous_edge_id), 1])
        
        found = False
        keys = list(self.beveled_parallel_edges_to_last_edge.keys())
        
        for previous_edge_id, value in self.beveled_parallel_edges_to_last_edge.items():
            for current_edge_id in value:
                if current_edge_id == edge_id:
                    relative_map['beveled_parallel_edges_to_last_edge'].append(keys.index(previous_edge_id))
                    relative_map['beveled_parallel_edges_to_last_edge'].append(value.index(current_edge_id))
                    
                    found = True
                    break
            
            if found:
                break
        
        keys = list(self.beveled_startend_edges_to_last_edge.keys())
        
        for previous_edge_id, value in self.beveled_startend_edges_to_last_edge.items():
            start_edge_id:int = value[0]
            end_edge_id:int = value[1]
            
            if start_edge_id == edge_id:
                relative_map['beveled_startend_edges_to_last_edge'] = [keys.index(previous_edge_id), 0]
                break
            
            if end_edge_id == edge_id:
                relative_map['beveled_startend_edges_to_last_edge'] = [keys.index(previous_edge_id), 1]
                break
        
        keys = list(self.unbeveled_edges.keys())
        for previous_edge_id, value in self.unbeveled_edges.items():
            current_edge_id:int = value
            
            if current_edge_id == edge_id:
                relative_map['unbeveled_edges'] = keys.index(previous_edge_id)
                break
        
        return relative_map
    
    def get_bevel_face_relative_map(self, face_id:int = 0) -> dict:
        """
        Returns every instance where the input face_id found on blender_mesh maps back to previous_blender_mesh
        
        Parameters
        ----------
        face_id: int
            The edge index found within blender_mesh
        
        Returns
        -------
            A dictionary of face_id from blender_mesh relatively mapped back to previous_blender_mesh.
            [
                beveled_faces_to_last_vertex:Array - Empty if not found, or a 2D array
                    [
                        0:
                            index of last vertex key,
                        1:
                            index of face_id
                    ],
                beveled_faces_to_last_edge:Array - Empty if not found, or a 2D array
                    [
                        0:
                            index of last edge key,
                        1:
                            index of face_id
                    ],
                unbeveled_faces:int
                    -1 if not found, or greater than or equal to zero if found, of which this value represents the index of the last face key.
            ]
        """
        relative_map:dict = {
            'beveled_faces_to_last_vertex': [],
            'beveled_faces_to_last_edge': [],
            'unbeveled_faces': -1,
        }
        
        found:bool = False
        keys:Array = list(self.beveled_faces_to_last_vertex.keys())
        
        for previous_vertex_id, value in self.beveled_faces_to_last_vertex.items():
            for current_face_id in value:
                if current_face_id == face_id:
                    relative_map['beveled_faces_to_last_vertex'] = [keys.index(previous_vertex_id), value.index(current_face_id)]
                    found = True
                    break
            
            if found:
                break
        
        found = False
        keys = list(self.beveled_faces_to_last_edge.keys())
        
        for previous_edge_id, value in self.beveled_faces_to_last_edge.items():
            for current_face_id in value:
                if current_face_id == face_id:
                    relative_map['beveled_faces_to_last_edge'].append(keys.index(previous_edge_id))
                    relative_map['beveled_faces_to_last_edge'].append(value.index(current_face_id))
                    
                    found = True
                    break
            
            if found:
                break
        
        keys = list(self.unbeveled_faces.keys())
        for previous_face_id, value in self.unbeveled_faces.items():
            current_face_id:int = value
            
            if current_face_id == face_id:
                relative_map['unbeveled_faces'] = keys.index(previous_face_id)
                break
        
        return relative_map
    
    def set_bmesh( self, blender_mesh:bmesh.types.BMesh ):
        self.blender_mesh = blender_mesh.copy()
    
    def set_empty( self ) -> None:
        self.blender_mesh = None
        self.previous_blender_mesh = None
        self.previous_selected_edges = []
        self.new_face_ids = []
        
        self.beveled_vertices_to_original_edge = {}
        self.beveled_vertices_to_last_edge = {}
        self.beveled_vertices_to_last_vertex = {}

        self.beveled_leftright_vertices_to_last_edge = {}
        self.beveled_leftright_vertices_to_original_edge = {}
        
        self.beveled_terminating_vertices_to_last_edge = {}
        self.beveled_terminating_vertices_to_original_edge = {}
        
        self.beveled_edges_to_original_edge = {}
        self.beveled_edges_to_last_edge = {}
        self.beveled_edges_to_last_vertex = {}
        
        self.beveled_leftright_edges_to_last_edge = {}
        self.beveled_leftright_edges_to_original_edge = {}
        
        self.beveled_terminating_edges_to_last_edge = {}
        self.beveled_terminating_edges_to_original_edge = {}
        
        self.beveled_parallel_edges_to_last_edge = {}
        self.beveled_parallel_edges_to_original_edge = {}
        
        self.beveled_startend_edges_to_original_edge = {}
        self.beveled_startend_edges_to_last_edge = {}
        
        self.beveled_leftright_edges_to_last_extend_edge = {}
        
        self.beveled_faces_to_original_edge = {}
        self.beveled_faces_to_last_edge = {}
        self.beveled_faces_to_last_vertex = {}
        
        self.beveled_terminating_faces_to_original_vertex = {}
        self.beveled_terminating_faces_to_last_vertex = {}
        
        self.unbeveled_vertices = {}
        self.unbeveled_edges = {}
        self.unbeveled_faces = {}

    def edge_is_bounding_bevel_edge( self, edge_id:int ) -> bool:
        for start_end_edges in self.beveled_startend_edges_to_last_edge:
            if edge_id in self.beveled_startend_edges_to_last_edge[ start_end_edges ]:
                return True
        
        for leftright_edge_group_indexes in self.beveled_leftright_edges_to_last_edge:
            for leftright_edge_group in self.beveled_leftright_edges_to_last_edge[ leftright_edge_group_indexes ]:
                if edge_id in leftright_edge_group:
                    return True
        
        return False
    
    def __str__( self ) -> str:
        stringed:str = ''
        
        stringed += 'blender_mesh: ' + str(self.blender_mesh) + '\n'
        stringed += 'previous_blender_mesh: ' + str(self.previous_blender_mesh) + '\n'
        stringed += 'previous_selected_edges : ' + str(self.previous_selected_edges) + '\n'
        stringed += 'new_face_ids: ' + str(self.new_face_ids) + '\n'
        stringed += 'beveled_vertices_to_original_edge: ' + str(self.beveled_vertices_to_original_edge) + '\n'
        stringed += 'beveled_vertices_to_last_edge: ' + str(self.beveled_vertices_to_last_edge) + '\n'
        stringed += 'beveled_vertices_to_last_vertex: ' + str(self.beveled_vertices_to_last_vertex) + '\n'
        stringed += 'beveled_leftright_vertices_to_last_edge: ' + str(self.beveled_leftright_vertices_to_last_edge) + '\n'
        stringed += 'beveled_leftright_vertices_to_original_edge: ' + str(self.beveled_leftright_vertices_to_original_edge) + '\n'
        stringed += 'beveled_terminating_vertices_to_last_edge: ' + str(self.beveled_terminating_vertices_to_last_edge) + '\n'
        stringed += 'beveled_terminating_vertices_to_original_edge: ' + str(self.beveled_terminating_vertices_to_original_edge) + '\n'
        stringed += 'beveled_edges_to_original_edge: ' + str(self.beveled_edges_to_original_edge) + '\n'
        stringed += 'beveled_edges_to_last_edge: ' + str(self.beveled_edges_to_last_edge) + '\n'
        stringed += 'beveled_edges_to_last_vertex: ' + str(self.beveled_edges_to_last_vertex) + '\n'
        stringed += 'beveled_leftright_edges_to_last_edge: ' + str(self.beveled_leftright_edges_to_last_edge) + '\n'
        stringed += 'beveled_leftright_edges_to_original_edge: ' + str(self.beveled_leftright_edges_to_original_edge) + '\n'
        stringed += 'beveled_terminating_edges_to_last_edge: ' + str(self.beveled_terminating_edges_to_last_edge) + '\n'
        stringed += 'beveled_terminating_edges_to_original_edge: ' + str(self.beveled_terminating_edges_to_original_edge) + '\n'
        stringed += 'beveled_parallel_edges_to_last_edge: ' + str(self.beveled_parallel_edges_to_last_edge) + '\n'
        stringed += 'beveled_parallel_edges_to_original_edge: ' + str(self.beveled_parallel_edges_to_original_edge) + '\n'
        stringed += 'beveled_startend_edges_to_original_edge: ' + str(self.beveled_startend_edges_to_original_edge) + '\n'
        stringed += 'beveled_startend_edges_to_last_edge: ' + str(self.beveled_startend_edges_to_last_edge) + '\n'
        stringed += 'beveled_leftright_edges_to_last_extend_edge: ' + str(self.beveled_leftright_edges_to_last_extend_edge) + '\n'
        stringed += 'beveled_faces_to_original_edge: ' + str(self.beveled_faces_to_original_edge) + '\n'
        stringed += 'beveled_faces_to_last_edge: ' + str(self.beveled_faces_to_last_edge) + '\n'
        stringed += 'beveled_faces_to_last_vertex: ' + str(self.beveled_faces_to_last_vertex) + '\n'
        stringed += 'beveled_terminating_faces_to_original_vertex: ' + str(self.beveled_terminating_faces_to_original_vertex) + '\n'
        stringed += 'beveled_terminating_faces_to_last_vertex: ' + str(self.beveled_terminating_faces_to_last_vertex) + '\n'
        stringed += 'unbeveled_vertices: ' + str(self.unbeveled_vertices) + '\n'
        stringed += 'unbeveled_edges: ' + str(self.unbeveled_edges) + '\n'
        stringed += 'unbeveled_faces: ' + str(self.unbeveled_faces) + '\n'
        
        return stringed

def map_face_edges(original_mesh:bmesh, new_mesh:bmesh, original_face_id:int, new_face_id:int, layer_map:simple_morph_219_layer_map, new_edges_to_ignore:Array, original_edges_to_ignore:Array ) -> Array:
    """
    Maps all edges, of original_face_id from original_mesh onto new_face_id from _new_mesh. This operation skips over new_edgess_to_ignore from new_face_id and original_edges_to_ignore from new_mesh
    
    Parameters
    ----------
    original_mesh : bmesh
        The original mesh that contains the face original_face_id
    
    new_mesh : bmesh
        The new mesh that contains the face new_face_id
    
    original_face_id : int
        ID of the face from original_mesh
    
    new_face_id : int
        ID of the face from new_mesh
    
    layer_map : simple_morph_219_layer_map
        A simple_morph_219_layer_map object. It *MUST* already have its beveled_leftright_edges_to_last_edge value calcualted.
    
    Returns
    -------
        An array of mapped edges. Each entry in the array is a 2D array:
            0:
                [
                    0: Id of the edge from original_face_id,
                    1: ID of the edge from new_face_id,
                ],
            ...,
            n:
                [
                    0: Id of the edge from original_face_id,
                    1: ID of the edge from new_face_id,
                ],
    """
    original_face_edge_ids_tmp:Array = [ edge.index for edge in original_mesh.faces[ original_face_id ].edges ]
    new_face_edge_ids_tmp:Array = [ edge.index for edge in new_mesh.faces[ new_face_id ].edges ]
    original_face_edge_ids:Array = []
    new_face_edge_ids:Array = []
    
    for edge_id in new_face_edge_ids_tmp:
        ignore:bool = False
        
        for leftright_edge_group_id in layer_map.beveled_leftright_edges_to_last_edge:
            if edge_id in layer_map.beveled_leftright_edges_to_last_edge[leftright_edge_group_id][0] or edge_id in layer_map.beveled_leftright_edges_to_last_edge[leftright_edge_group_id][1] or edge_id in new_edges_to_ignore:
                ignore = True
                break
        
        if not ignore:
            new_face_edge_ids.append(edge_id)
    
    mapped_edges:Array = []
    
    new_face_edge_ids_tmp = new_face_edge_ids.copy()
    new_face_edge_ids = []
    
    seed:bool = True
    closest_distance:float = 0.0
    closest_new_edge:int = 0
    closest_original_edge:int = 0
    original_face_edge_ids_tmp_copy:Array = original_face_edge_ids_tmp
    original_face_edge_ids_tmp = []
    
    for original_face_edge_id in original_face_edge_ids_tmp_copy:
        if original_face_edge_id not in original_edges_to_ignore:
            original_face_edge_ids_tmp.append(original_face_edge_id)
    
    for original_face_edge_id in original_face_edge_ids_tmp:
        new_edge, distance = get_closest_edge(original_mesh, new_mesh, original_face_edge_id, new_face_edge_ids_tmp)
        
        if seed:
            closest_distance = distance
            closest_new_edge = new_edge
            closest_original_edge = original_face_edge_id
            seed = False
        elif distance < closest_distance:
            closest_distance = distance
            closest_new_edge = new_edge
            closest_original_edge = original_face_edge_id
    
    new_edge_index:int = new_face_edge_ids_tmp.index(closest_new_edge)
    original_edge_index:int = original_face_edge_ids_tmp.index(closest_original_edge)
    
    for original_face_edge_id in original_face_edge_ids_tmp:
        mapped_edges.append([original_face_edge_ids_tmp[original_edge_index], new_face_edge_ids_tmp[new_edge_index]])
        new_edge_index -= 1
        original_edge_index -= 1
    
    return mapped_edges

#Finds the closest edge to mesh_1_edge_id from a list of edges, mesh_2_edge_list
def get_closest_edge(blender_mesh1:bmesh.types.BMesh, blender_mesh2:bmesh.types.BMesh, mesh_1_edge_id:int, mesh_2_edge_ids:Array) -> int | float:
    mesh_1_edge_center = ( blender_mesh1.edges[mesh_1_edge_id].verts[0].co + blender_mesh1.edges[mesh_1_edge_id].verts[1].co ) / 2
    
    shortest_distance:float = 0.0
    closest_edge:int = 0

    for mesh_2_edge_index, mesh_2_edge_id in enumerate(mesh_2_edge_ids):
        mesh_2_edge_center = ( blender_mesh2.edges[mesh_2_edge_id].verts[0].co + blender_mesh2.edges[mesh_2_edge_id].verts[1].co ) / 2
        distance:float = ( mesh_1_edge_center - mesh_2_edge_center ).length
        if mesh_2_edge_index == 0:
            closest_edge = mesh_2_edge_id
            shortest_distance = distance
        else:
            if distance < shortest_distance:
                shortest_distance = distance
                closest_edge = mesh_2_edge_id
    
    return closest_edge, shortest_distance

def map_beveled_mesh_to_previous_layer( original_mesh:bmesh, new_mesh:bmesh, new_faces:Array, new_layer_map:simple_morph_219_layer_map ) -> dict | dict | dict:
    """
    Maps all edges, vertices, and faces of new_mesh back to original_mesh. All vertices, edges, and faces that are part of the bevel operation are not included.
    
    Parameters
    ----------
    original_mesh : bmesh
        The pre-bevel mesh
    
    new_mesh : bmesh
        The post bevel mesh. This MUST be a mesh created via a bevel from previous_mesh
    
    new_faces : Array
        IDs of faces created from the bevel
    
    new_layer_map : simple_morph_219_layer_map
        layer map for the new mesh.
    
    Returns
    -------
        A tuple of 3 dictionaries with vertices, edges, and faces mapped back in the formats:
            vertices:
            {
                original_vertex_id_0 : new_vertex_id_0,
                ..........
                original_vertex_id_n : new_vertex_id_n,
            }
            edges:
            {
                original_edge_id_0 : new_edge_id_0,
                ..........
                original_edge_id_n : new_edge_id_n,
            }
            faces:
            {
                original_face_id_0 : new_face_id_0,
                ..........
                original_face_id_n : new_face_id_n,
            }
    """
    vertex_map:dict = {}
    edge_map:dict = {}
    face_map:dict = {}
    
    original_vertex_0_index:int = 0
    original_vertex_1_index:int = 0
    new_vertex_0_index:int = 0
    new_vertex_1_index:int = 0
    
    bounding_edges:Array = salowell_bpy_lib.get_bounding_edges_of_face_groups( new_mesh, new_faces )[3]
    bounding_vertices:Array = []
    new_edges_to_ignore:Array = []
    
    for bounding_edge_id in bounding_edges:
        if not new_layer_map.edge_is_startend_edge(bounding_edge_id):
            new_edges_to_ignore.append(bounding_edge_id)
            
        new_vertex_0_index = new_mesh.edges[bounding_edge_id].verts[0].index
        new_vertex_1_index = new_mesh.edges[bounding_edge_id].verts[1].index
        
        if new_vertex_0_index not in bounding_vertices:
            bounding_vertices.append(new_vertex_0_index)
        
        if new_vertex_1_index not in bounding_vertices:
            bounding_vertices.append(new_vertex_1_index)
    
    seed:bool = True
    
    previous_mesh_beveled_edge_ids:Array = []
    previous_mesh_beveled_vertex_ids:Array = []
    
    for previous_mesh_edge_id in new_layer_map.beveled_startend_edges_to_last_edge:
         previous_mesh_beveled_edge_ids.append(previous_mesh_edge_id)
    
    for previous_mesh_beveled_edge_id in previous_mesh_beveled_edge_ids:
        original_vertex_0_index = original_mesh.edges[previous_mesh_beveled_edge_id].verts[0].index
        original_vertex_1_index = original_mesh.edges[previous_mesh_beveled_edge_id].verts[1].index
        
        if original_vertex_0_index not in previous_mesh_beveled_vertex_ids:
            previous_mesh_beveled_vertex_ids.append(original_vertex_0_index)
        
        if original_vertex_1_index not in previous_mesh_beveled_vertex_ids:
            previous_mesh_beveled_vertex_ids.append(original_vertex_1_index)
    
    for previous_mesh_edge in new_layer_map.beveled_startend_edges_to_last_edge:
        original_mesh_faces = salowell_bpy_lib.get_faces_of_edge_bmesh( original_mesh, previous_mesh_edge )[1]
        new_mesh_faces:Array = [0, 0]
        new_mesh_faces[0] = salowell_bpy_lib.get_faces_of_edge_bmesh( new_mesh, new_layer_map.beveled_startend_edges_to_last_edge[previous_mesh_edge][0], -1, new_faces )[1][0]
        new_mesh_faces[1] = salowell_bpy_lib.get_faces_of_edge_bmesh( new_mesh, new_layer_map.beveled_startend_edges_to_last_edge[previous_mesh_edge][1], -1, new_faces )[1][0]
        
        face_to_startend_edge:dict = {}
        
        face_to_startend_edge[new_mesh_faces[0]] = new_layer_map.beveled_startend_edges_to_last_edge[previous_mesh_edge][0]
        face_to_startend_edge[new_mesh_faces[1]] = new_layer_map.beveled_startend_edges_to_last_edge[previous_mesh_edge][1]
        
        paired_faces = salowell_bpy_lib.pair_closest_faces( new_mesh, new_mesh_faces, original_mesh, original_mesh_faces )
        
        for paired_index in paired_faces:
            face_map[paired_index[1]] = paired_index[0]
            
            if seed:
                seed = False
                
                mapped_face_edges = map_face_edges(original_mesh, new_mesh, paired_index[1], paired_index[0], new_layer_map, new_edges_to_ignore, [])
                
                for mapped in mapped_face_edges:
                    if mapped[1] not in bounding_edges and mapped[0] not in new_layer_map.previous_selected_edges:
                        edge_map[mapped[0]] = mapped[1]
                        
                        original_vertex_0_index = original_mesh.edges[mapped[0]].verts[0].index
                        original_vertex_1_index = original_mesh.edges[mapped[0]].verts[1].index
                        new_vertex_0_index = new_mesh.edges[mapped[1]].verts[0].index
                        new_vertex_1_index = new_mesh.edges[mapped[1]].verts[1].index
                        
                        if original_vertex_0_index not in vertex_map and new_vertex_0_index not in bounding_vertices and original_vertex_0_index not in previous_mesh_beveled_vertex_ids:
                            vertex_map[original_vertex_0_index] = new_vertex_0_index
                        
                        if original_vertex_1_index not in vertex_map and new_vertex_1_index not in bounding_vertices and original_vertex_1_index not in previous_mesh_beveled_vertex_ids:
                            vertex_map[original_vertex_1_index] = new_vertex_1_index
    
    face_map_base:dict = face_map.copy()
    
    processed_new_faces:Array = []
    processed_original_faces:Array = []
    
    previous_face_queue:Array = []
    new_face_queue:Array = []
    
    seed = True
    
    for original_starting_face in face_map_base:
        new_starting_face = face_map_base[original_starting_face]
        
        if original_starting_face not in previous_face_queue:
            previous_face_queue.append(original_starting_face)
            new_face_queue.append(new_starting_face)
        
        queue_index:int = 0
        last_original_face:int = 0
        last_new_face:int = 0
        
        while len(previous_face_queue) > 0:
            original_face:int = previous_face_queue[0]
            del previous_face_queue[0]
            new_face:int = new_face_queue[0]
            del new_face_queue[0]
            
            if original_face in processed_original_faces:
                continue
            
            if seed:
                seed = False
                
                original_edge = None
                new_edge = None
                found_matching_edge:bool = False
                
                for original_edge in original_mesh.faces[original_face].edges:
                    for new_edge in new_mesh.faces[new_face].edges:
                        if original_edge.index in new_layer_map.beveled_startend_edges_to_last_edge:
                            if new_layer_map.beveled_startend_edges_to_last_edge[original_edge.index][0] == new_edge.index:
                                found_matching_edge = True
                            elif new_layer_map.beveled_startend_edges_to_last_edge[original_edge.index][1] == new_edge.index:
                                found_matching_edge = True
                        
                        if found_matching_edge:
                            break
                    
                    if found_matching_edge:
                        break
                
                original_edge_array:Array = []
                for edge in original_mesh.faces[original_face].edges:
                    original_edge_array.append(edge.index)
                
                new_edge_array:Array = []
                for edge in new_mesh.faces[new_face].edges:
                    new_edge_array.append(edge.index)
                
                mapped_face_edges = map_face_edges(original_mesh, new_mesh, original_face, new_face, new_layer_map, new_edges_to_ignore, [])
                
                for mapped in mapped_face_edges:
                    if mapped[1] not in bounding_edges and mapped[0] not in new_layer_map.previous_selected_edges:
                        edge_map[mapped[0]] = mapped[1]
                        
                        original_vertex_0_index = original_mesh.edges[mapped[0]].verts[0].index
                        original_vertex_1_index = original_mesh.edges[mapped[0]].verts[1].index
                        new_vertex_0_index = new_mesh.edges[mapped[1]].verts[0].index
                        new_vertex_1_index = new_mesh.edges[mapped[1]].verts[1].index
                        
                        if original_vertex_0_index not in vertex_map and new_vertex_0_index not in bounding_vertices and original_vertex_0_index not in previous_mesh_beveled_vertex_ids:
                            vertex_map[original_vertex_0_index] = new_vertex_0_index
                        
                        if original_vertex_1_index not in vertex_map and new_vertex_1_index not in bounding_vertices and original_vertex_1_index not in previous_mesh_beveled_vertex_ids:
                            vertex_map[original_vertex_1_index] = new_vertex_1_index
            else:
                new_mesh_edge_ids =  [new_mesh_edge.index for new_mesh_edge in new_mesh.faces[new_face].edges]
                
                closest_edge_id = get_closest_edge(original_mesh, new_mesh, original_mesh.faces[original_face].edges[0].index, new_mesh_edge_ids)
                
                mapped_face_edges = map_face_edges(original_mesh, new_mesh, original_face, new_face, new_layer_map, new_edges_to_ignore, [])
                
                for mapped in mapped_face_edges:
                    if mapped[1] not in bounding_edges and mapped[0] not in new_layer_map.previous_selected_edges:
                        edge_map[mapped[0]] = mapped[1]
                        
                        original_vertex_0_index = original_mesh.edges[mapped[0]].verts[0].index
                        original_vertex_1_index = original_mesh.edges[mapped[0]].verts[1].index
                        new_vertex_0_index = new_mesh.edges[mapped[1]].verts[0].index
                        new_vertex_1_index = new_mesh.edges[mapped[1]].verts[1].index
                        
                        if original_vertex_0_index not in vertex_map and new_vertex_0_index not in bounding_vertices and original_vertex_0_index not in previous_mesh_beveled_vertex_ids:
                            vertex_map[original_vertex_0_index] = new_vertex_0_index
                        
                        if original_vertex_1_index not in vertex_map and new_vertex_1_index not in bounding_vertices and original_vertex_1_index not in previous_mesh_beveled_vertex_ids:
                            vertex_map[original_vertex_1_index] = new_vertex_1_index
            
            if original_face not in face_map:
                face_map[original_face] = new_face
            
            mapped_face_edges = map_face_edges(original_mesh, new_mesh, original_face, new_face, new_layer_map, new_edges_to_ignore, [])
            
            for mapped_face_edge in mapped_face_edges:
                if mapped_face_edge[1] not in bounding_edges and mapped_face_edge[0] not in new_layer_map.previous_selected_edges:
                    original_faces_of_edge = salowell_bpy_lib.get_faces_of_edge_bmesh( original_mesh, mapped_face_edge[0] )[1]
                    new_faces_of_edge = salowell_bpy_lib.get_faces_of_edge_bmesh( new_mesh, mapped_face_edge[1] )[1]

                    paired_faces = salowell_bpy_lib.pair_closest_faces( original_mesh, original_faces_of_edge, new_mesh, new_faces_of_edge )
                    
                    for paired_face in paired_faces:
                        if paired_face[0] not in processed_original_faces and paired_face[1] not in processed_new_faces and paired_face[0] not in previous_face_queue and paired_face[1] not in new_face_queue and paired_face[1] not in new_faces:
                            new_face_queue.append(paired_face[1])
                            previous_face_queue.append(paired_face[0])
            
            last_original_face = original_face
            last_new_face = new_face
            processed_original_faces.append(original_face)
            processed_new_faces.append(new_face)
            queue_index += 1
        
        seed = True
    
    return vertex_map, edge_map, face_map

class simple_morph_219_object():
    """
    Stores a comprehensive history of any object generated through SimpleMorph219
    """
    base_blender_mesh:bmesh = None
    obj:object = None
    object_name:str = ''
    base_data_set:bool = False
    base_object_name:str = ''
    base_object:object = None
    base_vertices:int = 0
    base_edges:int = 0
    base_faces:int = 0
    
    layer_maps:dict = {}
    
    def __init__( self, object_name:str = '' ) -> None:
        self.set_base_object( object_name )
    
    def set_base_object( self, object_name:str ) -> bool:
        if salowell_bpy_lib.object_exists( object_name ):
            self.object_name = object_name
            self.obj = bpy.context.scene.objects[ object_name ]
            self.base_vertices = len( bpy.context.scene.objects[ object_name ].data.vertices )
            self.base_edges = len( bpy.context.scene.objects[ object_name ].data.edges )
            self.base_faces = len( bpy.context.scene.objects[ object_name ].data.polygons )
            self.base_data_set = True
            
            bpy.ops.object.mode_set( mode = 'OBJECT' )
            
            self.base_blender_mesh = bmesh.new()
            self.base_blender_mesh.from_mesh(bpy.context.scene.objects[ object_name ].data)
            
            return True
        
        return False
    
    #Retrieves the layer_map for layer_name. If it doesn't exist, it creates the map, adds it to the current simple morph 219 object AND returns the layer_map
    def get_layer_map_from_name( self, layer_name:str ) -> simple_morph_219_layer_map:
        if layer_name == ''    :
            return None
        
        if layer_name in self.layer_maps:
            return self.layer_maps[ layer_name ] 
        
        self.layer_maps[ layer_name ] = simple_morph_219_layer_map()
        
        return self.layer_maps[ layer_name ]
    
    def set_layer(self, layer_name:str, layer_map:simple_morph_219_layer_map ):
        self.layer_maps[ layer_name ] = layer_map

def create_if_not_exists_simple_morph_219_object(object_name) -> simple_morph_219_object:
    global simple_morph_219_object_list
    
    s_m_219_obj:simple_morph_219_object = None
    
    for obj in simple_morph_219_object_list:
        if obj.object_name == object_name:
            s_m_219_obj = obj
            break
    
    if s_m_219_obj is None:
        s_m_219_obj = simple_morph_219_object(object_name)
        simple_morph_219_object_list.append(s_m_219_obj)
    
    pie_menu_selection_data[2] = s_m_219_obj
    return s_m_219_obj

def layer_maps_to_array(layer_maps):
    layer_maps_array:Array = []
    
    if isinstance(layer_maps, list):
        for layer_map in layer_maps:
            layer_maps_array.append(layer_map)
    elif isinstance(layer_maps, dict):
        for layer_map in layer_maps.values():
            layer_maps_array.append(layer_map)
    else:
        layer_maps_array = layer_maps
    
    return layer_maps_array

def edge_to_edge_reference_bevel(edge_id, layer_maps:Array, blender_object:object, top_layer_prop_key_name:str) -> Array:
    """
    Returns the dynamic edges that the given edge_id maps to. This can be more than one dynamic edge.
    
    Parameters
    ----------
    edge_id : int
        The index of the edge you are trying to map.
    
    layer_maps : Array
        An array of layer_maps to use for this calculation.
    
    blender_object: object
        A blender object where all the layer properties reside.
    
    top_layer_prop_key_name : str
        The name of the layer that edge_id resides in.
    
    Returns
    -------
        An array of 4D arrays containing dynamic edges.
        [0 =>
            [Dynamic Edge
                0: int
                    0 = 0
                        The edge is unbeveled aka it maps back to layer_map.unbeveled_edges
                    0 = 1
                        The edge is a start edge from within layer_map.beveled_startend_edges_to_last_edge
                    0 = 2
                        The edge is an end edge from within layer_map.beveled_startend_edges_to_last_edge
                    0 = 3
                        The edge is an edge within layer_map.beveled_parallel_edges_to_last_edge
                    0 = 4
                        The edge is a left edge within layer_map.beveled_leftright_edges_to_last_edge
                    0 = 5
                        The edge is a right edge within layer_map.beveled_leftright_edges_to_last_edge
                1: int
                    The index that this edge belongs to from the property that index 0 of this dynamic selection points towards.
                    example: 0 = 2, 1 = 9. This means the edge is the 9th index of layer_map.beveled_startend_edges_to_last_edge
                2: float
                    Special case for determining how far into a layer_map.beveled_parallel_edges_to_last_edge selection is. Can be useful for mapping a selection after the smoothness of a bevel is updated.
                3: int
                    the layer_map index that edge_id belongs to.
            ]
        ...
            [
                ...
            ]
        n =>
            [
                ...
            ]
        ]
    """
    layer_maps = layer_maps_to_array(layer_maps)
    edge = edge_id
    
    real_corner_custom_prop_keys:Array = get_all_real_corner_custom_prop_keys(blender_object)
    real_corner_prop_index = real_corner_custom_prop_keys.index(top_layer_prop_key_name)
    selection_values:Array = []
    
    while real_corner_prop_index >= 0:
        selection_value:Array = [0, 0, 0.0, real_corner_prop_index]
        selection_value[3] = real_corner_prop_index
        layer_map = layer_maps[real_corner_prop_index]
        real_corner_prop_index -= 1
        is_unbeveled:bool = False
        previous_edge_id:int = 0
        
        for previous_edge in layer_map.unbeveled_edges:
            if edge == layer_map.unbeveled_edges[previous_edge]:
                previous_edge_id = previous_edge
                is_unbeveled = True
                break
        
        if is_unbeveled:
            layer_map_index:int = -1
            
            for previous_edge in layer_map.unbeveled_edges:
                layer_map_index += 1
                if layer_map.unbeveled_edges[previous_edge] == edge:
                    selection_value[0] = 0
                    selection_value[1] = layer_map_index
                    
                    selection_values.append(selection_value)
                    selection_value = [0, 0, 0.0, real_corner_prop_index + 1]
            
            if real_corner_prop_index >= 0:
                layer_map = layer_maps[real_corner_prop_index]
                edge = previous_edge_id
        else:
            layer_map_index:int = -1
            
            for previous_edge in layer_map.beveled_leftright_edges_to_last_edge:
                layer_map_index += 1
                    
                if edge in layer_map.beveled_leftright_edges_to_last_edge[previous_edge][0]:
                    selection_value[1] = layer_map_index
                    selection_value[0] = 4
                    selection_values.append(selection_value)
                    selection_value = [0, 0, 0.0, real_corner_prop_index + 1]
                
                if edge in layer_map.beveled_leftright_edges_to_last_edge[previous_edge][1]:
                    selection_value[1] = layer_map_index
                    selection_value[0] = 5
                    selection_values.append(selection_value)
                    selection_value = [0, 0, 0.0, real_corner_prop_index + 1]
            
            layer_map_index:int = -1
            
            for previous_edge in layer_map.beveled_parallel_edges_to_last_edge:
                layer_map_index += 1
                
                if edge in layer_map.beveled_parallel_edges_to_last_edge[previous_edge]:
                    selection_value[1] = layer_map_index
                    
                    if edge in layer_map.beveled_parallel_edges_to_last_edge[previous_edge]:
                        selection_value[2] = (layer_map.beveled_parallel_edges_to_last_edge[previous_edge].index(edge)) / (len(layer_map.beveled_parallel_edges_to_last_edge[previous_edge]) - 1)
                        selection_value[0] = 3
                        selection_values.append(selection_value)
                        selection_value = [0, 0, 0.0, real_corner_prop_index + 1]
            
            layer_map_index:int = -1
            
            for previous_edge in layer_map.beveled_startend_edges_to_last_edge:
                layer_map_index += 1
                
                if edge in layer_map.beveled_startend_edges_to_last_edge[previous_edge]:
                    selection_value[1] = layer_map_index
                    
                    if layer_map.beveled_startend_edges_to_last_edge[previous_edge][0] == edge:
                        selection_value[0] = 1
                        selection_values.append(selection_value)
                        selection_value = [0, 0, 0.0, real_corner_prop_index + 1]
                    elif layer_map.beveled_startend_edges_to_last_edge[previous_edge][1] == edge:
                        selection_value[0] = 2
                        selection_values.append(selection_value)
                        selection_value = [0, 0, 0.0, real_corner_prop_index + 1]
            break
    
    return selection_values

def edge_reference_to_edges(edge_reference:Array, simple_morph_219_obj:simple_morph_219_object, current_layer_prop_key_name:str) -> Array:
    real_corner_custom_prop_keys:Array = get_all_real_corner_custom_prop_keys(bpy.data.objects[simple_morph_219_obj.object_name])
    current_layer_prop_key_index:int = real_corner_custom_prop_keys.index(current_layer_prop_key_name)
    layer_prop_index:int = edge_reference[3]
    
    layer_map = simple_morph_219_obj.layer_maps[real_corner_custom_prop_keys[layer_prop_index]]
    edge_ids:Array = []
    
    if edge_reference[0] == 0:
        #Unbeveled Edge mapped back to where it was previously.
        edge_ids.append(list(layer_map.unbeveled_edges.values())[edge_reference[1]])
    if edge_reference[0] == 3:
        #Parallel edge formed from a bevel
        parallel_edges = list(layer_map.beveled_parallel_edges_to_last_edge.values())[edge_reference[1]]
        percent:float = edge_reference[2]
        edge_ids.append(parallel_edges[int(percent * (len(parallel_edges) - 1))])
    elif edge_reference[0] == 4:
        #Beveled left edges mapped back to the previous edge
        edge_ids = edge_ids + list(layer_map.beveled_leftright_edges_to_last_edge.values())[edge_reference[1]][0]
    elif edge_reference[0] == 5:
        #Beveled right edges mapped back to the previous edge
        edge_ids = edge_ids + list(layer_map.beveled_leftright_edges_to_last_edge.values())[edge_reference[1]][1]
    
    layer_prop_index += 1
    
    while layer_prop_index <= current_layer_prop_key_index:
        layer_map = simple_morph_219_obj.layer_maps[real_corner_custom_prop_keys[layer_prop_index]]
        
        edges_to_bevel = []
        
        for edge_id_index, edge_id in enumerate(edge_ids):
            for unbeveled_edge in layer_map.unbeveled_edges:
                if unbeveled_edge == edge_id:
                    edge_ids[edge_id_index] = layer_map.unbeveled_edges[unbeveled_edge]
                    break
        
        layer_prop_index += 1
    
    return edge_ids

class realCorner219States(Enum):
    NONE = 0
    SELECTING_EDGE = 1
    UPDATING_LAYER = 2

realCorner219CurrentState = realCorner219States.NONE
realCorner219LastUpdate = []
realCorner219SelectedBaseObjName:str = ''
realCorner219ModifiedObjName:str = ''
realcorner219HandleSelectDeselectFunctionLocked:bool = False
update_real_corner_bevel_values_locked:bool = False
real_corner_219_handle_edge_select_mode_click_locked:bool = False

def update_real_corner_bevel_values( op, context ):
    global update_real_corner_bevel_values_locked, realCorner219CurrentState, realCorner219States, realCorner219LastUpdate
    
    if update_real_corner_bevel_values_locked:
        return None
    
    objectNameToQueryPropertiesFrom:str = op.originalObjectName
    if realCorner219CurrentState == realCorner219States.UPDATING_LAYER and op.placeholderObjectName != '':
        objectNameToQueryPropertiesFrom = op.placeholderObjectName
    
    realCornerPropDict = realCornerBevelPropStringToDict( bpy.data.objects[ objectNameToQueryPropertiesFrom ][ op.real_corner_layer_name ] )
    
    if realCorner219CurrentState != realCorner219States.UPDATING_LAYER:
        realCornerPropDict[ 'edges' ] = selectedEdgesToCustomPropArray( bpy.data.objects[ op.originalObjectName ] )
    
    realCornerPropDict[ 'bevel_settings' ][ 'affect' ] = salowell_bpy_lib.bevel_affect_items[ op.affect ].value
    realCornerPropDict[ 'bevel_settings' ][ 'offset_type' ] = salowell_bpy_lib.bevel_offset_type_items[ op.offset_type ].value
    realCornerPropDict[ 'bevel_settings' ][ 'offset' ] = op.offset
    realCornerPropDict[ 'bevel_settings' ][ 'offset_pct' ] = op.offset_pct
    realCornerPropDict[ 'bevel_settings' ][ 'segments' ] = op.segments
    realCornerPropDict[ 'bevel_settings' ][ 'profile' ] = op.profile
    realCornerPropDict[ 'bevel_settings' ][ 'material' ] = op.material
    realCornerPropDict[ 'bevel_settings' ][ 'harden_normals' ] = op.harden_normals
    realCornerPropDict[ 'bevel_settings' ][ 'clamp_overlap' ] = op.clamp_overlap
    realCornerPropDict[ 'bevel_settings' ][ 'loop_slide' ] = op.loop_slide
    realCornerPropDict[ 'bevel_settings' ][ 'mark_seam' ] = op.mark_seam
    realCornerPropDict[ 'bevel_settings' ][ 'mark_sharp' ] = op.mark_sharp
    realCornerPropDict[ 'bevel_settings' ][ 'miter_outer' ] = salowell_bpy_lib.bevel_miter_outer_items[ op.miter_outer ].value
    realCornerPropDict[ 'bevel_settings' ][ 'miter_inner' ] = salowell_bpy_lib.bevel_miter_inner_items[ op.miter_inner ].value
    realCornerPropDict[ 'bevel_settings' ][ 'spread' ] = op.spread
    realCornerPropDict[ 'bevel_settings' ][ 'vmesh_method' ] = salowell_bpy_lib.bevel_vmesh_method_items[ op.vmesh_method ].value
    realCornerPropDict[ 'bevel_settings' ][ 'face_strength_mode' ] = salowell_bpy_lib.bevel_face_strength_mode_items[ op.face_strength_mode ].value
    realCornerPropDict[ 'bevel_settings' ][ 'profile_type' ] = salowell_bpy_lib.bevel_profile_type_items[ op.profile_type ].value
    
    realCorner219LastUpdate = [
        op.originalObjectName,
        op.real_corner_layer_name,
        realCornerPropDictToStringBevel( realCornerPropDict )
    ]
    
    return None

def real_corner_changed_selected_layer( uiCaller, context ):
    pass

def update_real_corner_selection_list( scene, context ):
    items = []
    selectedObject = bpy.context.selected_objects
    
    if len( selectedObject ) > 0:
        selectedObject = selectedObject[0]
        
        realCornerKeys = get_all_real_corner_custom_prop_keys( selectedObject )
        realCornerKeyLayer = 0
        
        for realCornerKey in realCornerKeys:
            realCornerKeyLayerStr = str( realCornerKeyLayer )
            
            operationType:str = ''
            
            if selectedObject[ realCorner219PropName + realCornerKeyLayerStr ].strip().startswith('219:0'):
                operationType = 'Bevel'
            
            items.append( ( realCornerKey, 'Layer ' + realCornerKeyLayerStr + ' - ' + operationType, 'Editing Real Corner layer ' + realCornerKeyLayerStr ) )
            realCornerKeyLayer += 1
    
    return items

def createRealCornerCustomPropKeyIfNoneExists( obj ):
    keyArray = get_all_real_corner_custom_prop_keys( obj )
    
    if len( keyArray ) == 0:
        keyArray.append(createNewCustomProperty(obj, realCorner219PropName, 'bevel'))
    
    return keyArray

def get_real_corner_custom_prop_key_index( obj, propKey):
    index:int = 0
    found:bool = False
    
    for key, value in obj.items():
        if type( value ) is str and value.startswith( '219:' ):
            if key == propKey:
                found = True
                break
            index += 1
    
    if not found:
        index = -1
    
    return index

def get_previous_real_corner_custom_prop_key( obj, prop_key ) -> str:
    prop_key_index:int = get_real_corner_custom_prop_key_index( obj, prop_key )
    
    if prop_key_index == 0:
        return ''
    
    prop_key_array = get_all_real_corner_custom_prop_keys( obj )
    
    return prop_key_array[ prop_key_index - 1 ]

def get_all_real_corner_custom_prop_keys( obj ):
    realCornerKeys = []
    
    for key, value in obj.items():
        if type( value ) is str and value.startswith( '219:' ) and key.startswith( realCorner219PropName ) :
            realCornerKeys.append( key )
    
    return realCornerKeys

def normalizeRealCornerCustomPropertyNames( obj ):
    values = []
    
    index:int = 0
    
    for keyValueTuple in list( obj.items() ):
        key = keyValueTuple[0]
        value = keyValueTuple[1]
        
        if key.startswith( realCorner219PropName ):
            values.append( value )
            del obj[ key ]
            index += 1
    
    index = 0
    for value in values:
        obj[ realCorner219PropName + str( index ) ] = value
        index += 1

def createNewCustomProperty(obj:object, keyName:str, type:str):
    type = type.lower()
    normalizeRealCornerCustomPropertyNames( obj )
    suffix = 0
    keyNameWithSuffix = keyName + str( suffix )
    
    for key, _ in obj.items():
        if key == keyNameWithSuffix:
            suffix += 1
        elif key.startswith( keyName ):
            break
        
        keyNameWithSuffix = keyName + str( suffix )
    
    propDictionary:dict = {}
    
    if type == 'bevel':
        propDictionary = realCornerPropDictToStringBevel(createEmptyRealCornerPropDict('bevel'))
    
    obj[keyNameWithSuffix] = propDictionary
    
    return keyNameWithSuffix

bpy.types.Scene.realCorner219Layers:bpy.props.EnumProperty = bpy.props.EnumProperty(
    name = "Layer",
    description = "Choose layer", 
    items = update_real_corner_selection_list,
    update = real_corner_changed_selected_layer
)

def createSupportingEdgeLoopsAroundSelectedFaces( obj, supporting_edge_loop_length:float = 0.01 ) -> None:
    initial_selected_face_indexes = salowell_bpy_lib.get_selected_faces( obj )[1]
    bounding_edges_indexes:Array = salowell_bpy_lib.get_bounding_edges_of_selected_face_groups( bpy.context.selected_objects[0] )[1]

    for face_group in bounding_edges_indexes:
        for edge_group in face_group:
            for edge in edge_group:
                bpy.ops.object.mode_set( mode = 'EDIT')
                bpy.ops.mesh.select_all( action = 'DESELECT' )
                salowell_bpy_lib.select_faces( obj, initial_selected_face_indexes )
                
                unselected_faces_of_bounding_edge:Array = salowell_bpy_lib.get_faces_of_edge( bpy.context.selected_objects[0], edge, -1 )[1]
                
                edges_to_split:Array = []
                source_vertex:Array = []
                
                #Looping through both vertices of this bounding edge.
                for vertex in bpy.context.selected_objects[0].data.edges[ edge ].vertices:
                    bpy.ops.object.mode_set( mode = 'EDIT')
                    bpy.ops.mesh.select_all( action = 'DESELECT' )
                    salowell_bpy_lib.select_faces( obj, initial_selected_face_indexes )
                    #When selecting the faces, if we don't toggle back to edit then object mode the faces will be selected but the edges will not be!! Blender plz
                    bpy.ops.object.mode_set( mode = 'EDIT')
                    bpy.ops.object.mode_set( mode = 'OBJECT')
                    
                    edges_of_vertex = salowell_bpy_lib.get_edges_of_vertex( bpy.context.selected_objects[0].data, vertex, -1 )
                    
                    #Looping through the unbeveled edges connected to one of the vertices of this bounding edge.
                    for edge_of_vertex in edges_of_vertex:
                        unselected_faces_touching_unbeveled_edge = salowell_bpy_lib.get_faces_of_edge( bpy.context.selected_objects[0], edge_of_vertex, -1 )[1]
                        
                        for unselected_face_touching_unbeveled_edge in unselected_faces_touching_unbeveled_edge:
                            if unselected_face_touching_unbeveled_edge in unselected_faces_of_bounding_edge:
                                #Found the edge that is touching the same face as the outer bounding edge.
                                edges_to_split.append( edge_of_vertex )
                                source_vertex.append( vertex )
                
                verts_to_join:Array = []
                
                for edge_to_split_index, edge_to_split in enumerate( edges_to_split ):
                    source_vertex_index:int = 0
                    destination_vertex_index:int = 1
                    
                    if bpy.context.selected_objects[0].data.edges[ edge_to_split ].vertices[1] == source_vertex[ edge_to_split_index ]:
                        source_vertex_index:int = 1
                        destination_vertex_index:int = 0
                    
                    bpy.context.selected_objects[0].data.edges[ edge_to_split ]
                    length = mathutils.Vector( bpy.context.selected_objects[0].data.vertices[ destination_vertex_index ].co - bpy.context.selected_objects[0].data.vertices[ source_vertex_index ].co ).length
                    
                    if length <= supporting_edge_loop_length:
                        verts_to_join.append( bpy.context.selected_objects[0].data.edges[ edge_to_split ].vertices[ destination_vertex_index ] )
                    else:
                        pre_split_edge = bpy.context.selected_objects[0].data.edges[ edge_to_split ]
                        bpy.context.selected_objects[0].data.vertices[ pre_split_edge.vertices[ destination_vertex_index ] ].co
                        move_vector:vertex = bpy.context.selected_objects[0].data.vertices[ pre_split_edge.vertices[ destination_vertex_index ] ].co - bpy.context.selected_objects[0].data.vertices[ pre_split_edge.vertices[ source_vertex_index ] ].co
                        move_vector.normalize()
                        new_vertex_position = bpy.context.selected_objects[0].data.vertices[ pre_split_edge.vertices[ source_vertex_index ] ].co + move_vector * supporting_edge_loop_length
                        source_vertex_index_id = bpy.context.selected_objects[0].data.vertices[ pre_split_edge.vertices[ source_vertex_index ] ].index
                        destination_vertex_index_id = bpy.context.selected_objects[0].data.vertices[ pre_split_edge.vertices[ destination_vertex_index ] ].index
                        
                        bpy.ops.object.mode_set( mode = 'EDIT')
                        bpy.ops.mesh.select_all( action = 'DESELECT' )
                        bpy.ops.object.mode_set( mode = 'OBJECT')
                        
                        bpy.context.selected_objects[0].data.edges[ edge_to_split ].select = True
                        
                        bpy.ops.object.mode_set( mode = 'EDIT' )
                        bpy.ops.mesh.subdivide( number_cuts = 1 )
                        bpy.ops.object.mode_set( mode = 'OBJECT')
                        
                        split_vertices_indexes = [ v for v in bpy.context.selected_objects[0].data.vertices if v.select ]
                        split_edges = [ e.index for e in bpy.context.selected_objects[0].data.edges if e.select ]
                        
                        for split_vertex in split_vertices_indexes:
                            if split_vertex.index != source_vertex_index_id and split_vertex.index != destination_vertex_index_id:
                                split_vertex.co = new_vertex_position
                                verts_to_join.append( split_vertex.index )
                                break
                
                bpy.ops.object.mode_set( mode = 'EDIT' )
                bpy.ops.mesh.select_all( action = 'DESELECT' )
                bpy.ops.object.mode_set( mode = 'OBJECT' )
                
                for vert_to_join_index in verts_to_join:
                    bpy.context.selected_objects[0].data.vertices[ vert_to_join_index ].select = True
                
                bpy.ops.object.mode_set( mode = 'EDIT' )
                bpy.ops.mesh.vert_connect_path()

class SIMPLE_MORPH_219_REAL_CORNER_QuickOps( Operator ):
    bl_idname = 'realcorner219.real_corner_quickops_op'
    bl_label = 'Real Corner 219 - Quick Operators'
    bl_description = 'Simplemorph_219_op_description'
    
    action: EnumProperty(
        items = [
            ( "TEST_QUICK", "Test Quick", "Test Quick" ),
            ( "APPLY_REAL_CORNER_CHANGES", "Apply Real Corner Changes", "This is used to apply any recent real corner changes that were made" ),
            ( "TURN_ON_SELECT_MODE", "Turn On Real Corner 219 Edge Select", "Turns on the Real Corner 219 Edge Select mode."),
            ( "TURN_OFF_AND_SAVE_SELECT_MODE", "Turn Off Real Corner 219 Edge Select and save", "Turns off the Real Corner 219 Edge Select mode and saves the currently selected edges."),
        ]
    )
    
    def execute( self, context ):
        global realCorner219CurrentState, realCorner219SelectedBaseObjName, realCorner219ModifiedObjName, realcorner219HandleSelectDeselectFunctionLocked
        
        if self.action == 'TEST_QUICK':
            previous_mesh_name = 'Cube'
            new_mesh_name = 'Cube.001'
            bevel_segment_count = 3
            
            previous_mesh = bpy.data.objects[previous_mesh_name].data
            new_mesh = bpy.data.objects[new_mesh_name].data
            
            previous_bmesh = salowell_bpy_lib.mesh_to_bmesh(previous_mesh)
            new_bmesh = salowell_bpy_lib.mesh_to_bmesh(new_mesh)
            
            previous_unbeveled_edge_ids_in:Array = [v.index for v in previous_mesh.edges if v.select]
            new_bevel_face_ids_in:Array = [v.index for v in new_mesh.polygons if v.select]
            
            print(salowell_bpy_lib.generate_bevel_layer_map( new_bmesh, previous_bmesh, new_bevel_face_ids_in, previous_unbeveled_edge_ids_in, bevel_segment_count ))
            #generated_meshes1, selected_face_objects1, selected_face_indexes1, selected_edge_objects1, selected_edge_indexes1, selected_vertex_objects1, selected_vertices1 = gen_real_corner_meshes( bpy.data.objects['Cube'], 'realCorner219_0' )
            #generated_meshes2, selected_face_objects2, selected_face_indexes2, selected_edge_objects2, selected_edge_indexes2, selected_vertex_objects2, selected_vertices2 = gen_real_corner_meshes( bpy.data.objects['Cube'], 'realCorner219_1' )
            #generated_meshes3, selected_face_objects3, selected_face_indexes3, selected_edge_objects3, selected_edge_indexes3, selected_vertex_objects3, selected_vertices3 = gen_real_corner_meshes( bpy.data.objects['Cube'], 'realCorner219_2' )
            #generated_meshes4, selected_face_objects4, selected_face_indexes4, selected_edge_objects4, selected_edge_indexes4, selected_vertex_objects4, selected_vertices4 = gen_real_corner_meshes( bpy.data.objects['Cube'], 'realCorner219_3' )
            return { 'FINISHED' }
            base_blender_mesh = salowell_bpy_lib.mesh_to_bmesh(bpy.data.objects['Cube'].data)
            
            generated_meshes1[0].to_mesh(bpy.data.objects['Cube.000'].data)
            bpy.data.objects['Cube.000'].data.update()
            
            generated_meshes2[0].to_mesh(bpy.data.objects['Cube.001'].data)
            bpy.data.objects['Cube.001'].data.update()
            
            generated_meshes3[0].to_mesh(bpy.data.objects['Cube.001'].data)
            bpy.data.objects['Cube.002'].data.update()
            
            generated_meshes4[0].to_mesh(bpy.data.objects['Cube.001'].data)
            bpy.data.objects['Cube.003'].data.update()
            
            propDic1 = realCornerPropIndexToDict( bpy.data.objects['Cube'], 'realCorner219_0' )
            propDic2 = realCornerPropIndexToDict( bpy.data.objects['Cube'], 'realCorner219_1' )
            propDic3 = realCornerPropIndexToDict( bpy.data.objects['Cube'], 'realCorner219_2' )
            
            layer_map1 = salowell_bpy_lib.generate_bevel_layer_map( generated_meshes1[0], base_blender_mesh, selected_face_indexes1[0], propDic1['edges'] )
            layer_map2 = salowell_bpy_lib.generate_bevel_layer_map( generated_meshes2[0], generated_meshes1[0], selected_face_indexes2[0], propDic2['edges'] )
            layer_map3 = salowell_bpy_lib.generate_bevel_layer_map( generated_meshes3[0], generated_meshes2[0], selected_face_indexes3[0], propDic3['edges'] )
            return { 'FINISHED' }
            salowell_bpy_lib.generate_bevel_layer_map( salowell_bpy_lib.mesh_to_bmesh(bpy.data.objects['Cube.068'].data), salowell_bpy_lib.mesh_to_bmesh(bpy.data.objects['Cube.065'].data), [20, 19, 18, 17, 25, 26, 27, 28, 33, 34, 35, 36, 9, 10, 11, 12, 5, 6, 7, 8, 29, 30, 31, 32, 13, 14, 15, 16, 24, 23, 22, 21], [0, 2, 4, 5, 7, 8, 10, 11] )
            
            test_arry:Array = [4, 5, 0, 2]
            test_arry = [8, 2, 5, 6, 3, 0]
            test_arry = [8, 2, 7, 6, 3, 0]
            test_arry = [6, 7, 0, 4, 10, 2, 11]
            layer_properties:dict = realCornerPropIndexToDict(bpy.context.selected_objects[0], context.scene.realCorner219Layers)
            layer_index:int = get_real_corner_custom_prop_key_index(bpy.context.selected_objects[0], context.scene.realCorner219Layers)
            custom_prop_keys:Array = get_all_real_corner_custom_prop_keys(bpy.context.selected_objects[0])
            previous_layer_key:str = custom_prop_keys[layer_index - 1]
            previous_mesh = salowell_bpy_lib.mesh_to_bmesh(bpy.context.selected_objects[0].data)

            current_meshes, _, new_face_ids, _, selected_edge_indexes, _, selected_vertices = gen_real_corner_meshes( bpy.context.selected_objects[0], context.scene.realCorner219Layers )
            
            salowell_bpy_lib.get_grouped_faces( current_meshes[-1], new_face_ids[0] )

            return { 'FINISHED' }
        if self.action == 'APPLY_REAL_CORNER_CHANGES':
            pass
        elif self.action == 'TURN_ON_SELECT_MODE':
            realcorner219HandleSelectDeselectFunctionLocked = True
            selectedObject = context.selected_objects
            
            if len( selectedObject ) == 0:
                return { 'CANCELLED' }
            
            selectedObject = selectedObject[0]
            
            realCorner219CurrentState = realCorner219States.SELECTING_EDGE
            realCorner219SelectedBaseObjName = selectedObject.name
            bpy.ops.object.mode_set( mode = 'OBJECT')
            salowell_bpy_lib.isolate_object_select( bpy.context.object )
            bpy.ops.object.duplicate()
            realCorner219ModifiedObjName = context.object.name
            
            salowell_bpy_lib.isolate_object_select( bpy.data.objects[realCorner219ModifiedObjName] )
            bpy.data.objects[ realCorner219ModifiedObjName ][ simplemorph219.simpleMorph219BaseName ] = False
            bpy.ops.object.mode_set( mode = 'EDIT')
            
            blender_mesh = genRealCornerMeshAtPrevIndex( bpy.data.objects[ realCorner219ModifiedObjName ], context.scene.realCorner219Layers )[0]
            
            if len( blender_mesh ) == 0:
                blender_mesh = salowell_bpy_lib.mesh_to_bmesh(bpy.data.objects[ realCorner219ModifiedObjName ].data)
            else:
                blender_mesh = blender_mesh[-1]
            
            realCorner219ModifiedObjName = context.selected_objects[0].name
            realcorner219HandleSelectDeselectFunctionLocked = False
            bpy.data.objects[ realCorner219SelectedBaseObjName ].hide_viewport = True
            
            bpy.ops.object.mode_set( mode = 'OBJECT')
            blender_mesh.to_mesh(bpy.data.objects[realCorner219ModifiedObjName].data)
            bpy.data.objects[realCorner219ModifiedObjName].update_from_editmode()
            bpy.ops.object.mode_set( mode = 'EDIT')
            realcorner219HandleSelectDeselectFunctionLocked = False
        elif self.action == 'TURN_OFF_AND_SAVE_SELECT_MODE':
            realcorner219HandleSelectDeselectFunctionLocked = True
            originalObject = None
            modifiedObject = None
            
            for obj in bpy.context.scene.objects:
                if obj.name == realCorner219SelectedBaseObjName:
                    originalObject = obj
                    break
            
            for obj in bpy.context.scene.objects:
                if obj.name == realCorner219ModifiedObjName:
                    modifiedObject = obj
                    break
            
            if originalObject is not None and modifiedObject is not None:
                realCornerPropDict = realCornerPropIndexToDict( originalObject, context.scene.realCorner219Layers )
                
                if context.scene.realCorner219Layers == realCorner219PropName + '0':
                    realCornerPropDict[ 'edges' ] = selectedEdgesToCustomPropArray( modifiedObject )
                    realCornerPropDict[ 'edge_references' ] = []
                else:
                    realCornerPropDict[ 'edges' ] = []
                
                originalObject[ context.scene.realCorner219Layers ] = realCornerPropDictToStringBevel( realCornerPropDict )
            
            if modifiedObject is not None:
                salowell_bpy_lib.isolate_object_select( modifiedObject )
                bpy.ops.object.delete()
            
            if originalObject is not None:
                salowell_bpy_lib.isolate_object_select( bpy.context.scene.objects[ realCorner219SelectedBaseObjName ] )
                bpy.context.scene.objects[ realCorner219SelectedBaseObjName ].hide_viewport = False
                salowell_bpy_lib.isolate_object_select( originalObject )
            
            realCorner219CurrentState = realCorner219States.NONE
            realCorner219SelectedBaseObjName = ''
            realCorner219ModifiedObjName = ''
            realcorner219HandleSelectDeselectFunctionLocked = False
        
        return { 'FINISHED' }

def get_edges_from_dynamic_edge(dynamic_edge:Array, blender_object:object) -> Array:
    """
        Retrieves all of the edges that belong to the given dynamic_edge.
        NOTE: The layer index is determined by dynamic_edge[3]. This represents the layer at which the edges are selected/mapped to the dynamic edge. It's generally a layer below where the dynamic edges are saved.
        WARNING: This function generates meshes and layer maps every time it's ran and technically works as a wrapper for get_edges_from_dynamic_edge_fast(), so consider using that function instead.
        
        Parameters
        ----------
            dynamic_edge: Array
                The dynamic edge to use as a selection. See the return result of edge_to_edge_reference_bevel() for a reference on how this array is formatted.
            
            blender_object: obj
                The Blender Object that will be used as the base object. This object must contain all the simple morph properties.
        
        Returns
        -------
            edge_ids: Array
                An array of all edge IDs
    """
    global realCorner219PropName
    
    gen_real_corner_meshes_result:Array = gen_real_corner_meshes(blender_object, realCorner219PropName + str(dynamic_edge[3]))
    
    edge_ids = get_edges_from_dynamic_edge_fast(dynamic_edge, gen_real_corner_meshes_result[7][dynamic_edge[3]])
    
    return edge_ids

def get_edges_from_dynamic_edge_fast(dynamic_edge:Array, layer_map:simple_morph_219_layer_map) -> Array:
def get_edge_ids_from_dynamic_edge(dynamic_edge:Array, layer_maps:Array) -> Array:
    """
        Retrieves all of the edges ids that this dynamic_edge directly points towards/references. This does not do a full tree search for all edges that this one "technically" references.
        
        Parameters
        ----------
            dynamic_edge: Array
                The dynamic edge to use as a selection. See the return result of edge_to_edge_reference_bevel() for a reference on how this array is formatted.
            
            layer_maps: Array
                An array of simple_morph_219_layer_map objects. Must be in correct order.
        
        Returns
        -------
            edge_ids: Array
                An array of all edge IDs/indexes
    """
    layer_maps = layer_maps_to_array(layer_maps)
    
    edge_ids:Array = []
    layer_map:simple_morph_219_layer_map = layer_maps[dynamic_edge[3]]
    
    match dynamic_edge[0]:
        case 0:
            edge_ids.append(list(layer_map.unbeveled_edges.values())[dynamic_edge[1]])
        case 1:
            edge_ids.append(list(layer_map.beveled_startend_edges_to_last_edge.values())[dynamic_edge[1]][0])
        case 2:
            edge_ids.append(list(layer_map.beveled_startend_edges_to_last_edge.values())[dynamic_edge[1]][1])
        case 3:
            edge_ids = edge_ids + list(layer_map.beveled_parallel_edges_to_last_edge.values())[dynamic_edge[1]]
        case 4:
            edge_ids = edge_ids + list(layer_map.beveled_leftright_edges_to_last_edge.values())[dynamic_edge[1]][0]
        case 5:
            edge_ids = edge_ids + list(layer_map.beveled_leftright_edges_to_last_edge.values())[dynamic_edge[1]][1]
    
    return edge_ids

def get_low_dynamic_edge_from_dynamic_edge(dynamic_edge:Array, layer_maps:Array, blender_object:object) -> Array:
    """
        This takes a dynamic edge[dynamic_edge] and traverses down the layer maps until it finds the lowest dynamic edge that the input dynamic_edge references.
        
        Parameters
        ----------
            dynamic_edge: Array
                The dynamic edge to use as a starting point. See the return result of edge_to_edge_reference_bevel() for a reference on how this array is formatted.
            
            layer_maps: Array
                An array of simple_morph_219_layer_map objects. Must be in correct order.
            
            blender_object: object
                The original belnder object that all the layer_maps were generated from, aka the base layer Blender Object.
        
        Returns
        -------
            layer_dynamic_edge: Array
                a Dynamic Edge that is the lowest possible dynamic edge referened by the original dynamic_edge input.
    """
    global realCorner219PropName
    
    layer_maps = layer_maps_to_array(layer_maps)
    
    layer_dynamic_edge = dynamic_edge
    current_index = layer_dynamic_edge[3]
    high_index = current_index
    
    while True:
        layer_map = layer_maps[current_index]
        
        if layer_dynamic_edge[0] == 0:#layer_map.unbeveled_edges
            if current_index != high_index:
                layer_dynamic_edge = edge_to_edge_reference_bevel(previous_edge_id, layer_maps, blender_object, realCorner219PropName + str(layer_dynamic_edge[3] - 1))
                layer_dynamic_edge = layer_dynamic_edge[0]
            
            previous_edge_id = list(layer_map.unbeveled_edges.keys())[layer_dynamic_edge[1]]
        else:
            break
        
        current_index -= 1
        
        if current_index < 0:
            break
    
    return layer_dynamic_edge

def get_edge_ids_at_layer_from_dynamic_edge_fast(dynamic_edge:Array, layer_maps:Array, target_layer_index:int, blender_object:object):
    """
        This takes a dynamic edge[dynamic_edge] and a layer index[target_layer_index] and calculates all the edge IDs that dynamic_edge points to from within the layer target_layer_index.
        
        Parameters
        ----------
            dynamic_edge: Array
                The dynamic edge to use as a main reference. See the return result of edge_to_edge_reference_bevel() for a reference on how this array is formatted.
            
            layer_maps: Array
                An array of simple_morph_219_layer_map objects. Must be in correct order.
            
            target_layer_index: int
                The layer index where the edge ids will be calculated relative to the given dynamic_edge.
            
            blender_object: object
                The original belnder object that all the layer_maps were generated from, aka the base layer Blender Object.
        
        Returns
        -------
            edge_indexes: Array
                All the edge index within the given target_layer_index that dynamic_edge technically references.
    """
    global realCorner219PropName
    
    layer_maps = layer_maps_to_array(layer_maps)
    
    current_layer_map_index:int = dynamic_edge[3]
    current_layer_dynamic_edges:Array = [dynamic_edge]
    
    layer_edge_ids:Array = []
    
    while current_layer_map_index <= target_layer_index:
        layer_edge_ids = []
        
        for current_layer_dynamic_edge in current_layer_dynamic_edges:
            layer_edge_ids += get_edge_ids_from_dynamic_edge(current_layer_dynamic_edge, layer_maps)
        
        current_layer_map_index += 1
        
        current_layer_dynamic_edges = []
        
        tmp:Array = []
        
        [x for x in layer_edge_ids if not (x in tmp or tmp.append(x))]
        
        layer_edge_ids = tmp
        
        if current_layer_map_index <= target_layer_index:
            for layers_edge_id in layer_edge_ids:
                new_mapped_layer_edge_ids:Array = get_layer_map_edges_from_previous_layer_map_edge(layers_edge_id, current_layer_map_index - 1, layer_maps)
                
                for new_mapped_layer_edge_id in new_mapped_layer_edge_ids:
#TODO: Once again this [0] only retrieves the first result and ignores others. Eventually others need to be considered or perhaps not?????
                    current_layer_dynamic_edges.append(edge_to_edge_reference_bevel(new_mapped_layer_edge_id, layer_maps, blender_object, realCorner219PropName+ str(current_layer_map_index))[0])
    
    seen = set()
    
    [x for x in layer_edge_ids if not (x in seen or seen.add(x))]
    
    return layer_edge_ids

def get_layer_map_edges_from_previous_layer_map_edge(previous_layer_map_edge_id:int, previous_layer_map_index:int, layer_maps:Array) -> Array:
    """
        Given an edge id[previous_layer_map_edge_id] from the previous layer [denoted by previous_layer_map_index], this finds all the edge IDS that it maps to on the new layer[previous_layer_map_index + 1]

        Parameters
        ----------
            previous_layer_map_edge_id: int
                ID of the edge on the previous layer
            
            previous_layer_map_index: int
                Index of the previous layer.
            
            layer_maps: Array
                 An array of simple_morph_219_layer_map objects. Must be in correct order.
        
        Returns
        -------
            edge_indexes: Array
                All the edge indexes/IDs within the current layer that map back to the Edge ID[previous_layer_map_edge_id] on the previous layer[previous_layer_map_index].
    """
    layer_maps = layer_maps_to_array(layer_maps)
    
    edge_indexes:Array = []
    current_layer_map_index:int = previous_layer_map_index + 1
    current_layer_map = layer_maps[current_layer_map_index]
    
    if previous_layer_map_edge_id in current_layer_map.beveled_leftright_edges_to_last_edge.keys():
        edge_indexes = edge_indexes + current_layer_map.beveled_leftright_edges_to_last_edge[previous_layer_map_edge_id][0]
        edge_indexes = edge_indexes + current_layer_map.beveled_leftright_edges_to_last_edge[previous_layer_map_edge_id][1]
    
    if previous_layer_map_edge_id in current_layer_map.beveled_parallel_edges_to_last_edge.keys():
        edge_indexes = edge_indexes + current_layer_map.beveled_parallel_edges_to_last_edge[previous_layer_map_edge_id]
    
    if previous_layer_map_edge_id in current_layer_map.beveled_startend_edges_to_last_edge.keys():
        edge_indexes = edge_indexes + current_layer_map.beveled_startend_edges_to_last_edge[previous_layer_map_edge_id]
    
    if previous_layer_map_edge_id in current_layer_map.unbeveled_edges.keys():
        edge_indexes.append(current_layer_map.unbeveled_edges[previous_layer_map_edge_id])
    
    seen:Array = []
    
    [x for x in edge_indexes if not (x in seen or seen.append(x))]
    
    edge_indexes = seen
    
    return edge_indexes
    
    """
        Retrieves all of the edges that belong to the given dynamic_edge.
        NOTE: The layer index is determined by dynamic_edge[3]. This represents the layer at which the edges are selected/mapped to the dynamic edge. It's generally a layer below where the dynamic edges are saved.
        WARNING: consider using this function over get_edges_from_dynamic_edge(), as this one does not have to generate a full bevel map and all its meshes every time it runs.
        
        Parameters
        ----------
            dynamic_edge: Array
                The dynamic edge to use as a selection. See the return result of edge_to_edge_reference_bevel() for a reference on how this array is formatted.

            layer_map: simple_morph_219_layer_map
                
        
        Returns
        -------
            edge_indexes: Array
                An array of all edge indexes
            
            edge_objects: Array
                An array of all edge objects
    """
    edge_ids:Array = []
    
    if dynamic_edge[0] == 0:
        previous_edge_ids:Array = list(layer_map.unbeveled_edges.keys())
        edge_ids.append(layer_map.unbeveled_edges[previous_edge_ids[dynamic_edge[1]]])
    elif dynamic_edge[0] == 1:
        previous_edge_ids:Array = list(layer_map.beveled_startend_edges_to_last_edge.keys())
        edge_ids.append(layer_map.beveled_startend_edges_to_last_edge[previous_edge_ids[dynamic_edge[1]]][0])
    elif dynamic_edge[0] == 2:
        previous_edge_ids:Array = list(layer_map.beveled_startend_edges_to_last_edge.keys())
        edge_ids.append(layer_map.beveled_startend_edges_to_last_edge[previous_edge_ids[dynamic_edge[1]]][1])
    elif dynamic_edge[0] == 3:
#TODO: The percentage of dynamic_edge[2] is not yet used.
        previous_edge_ids:Array = list(layer_map.beveled_parallel_edges_to_last_edge.keys())
        edge_ids = layer_map.beveled_parallel_edges_to_last_edge[previous_edge_ids[dynamic_edge[1]]]
    elif dynamic_edge[0] == 4:
        previous_edge_ids:Array = list(layer_map.beveled_leftright_edges_to_last_edge.keys())
        edge_ids = layer_map.beveled_leftright_edges_to_last_edge[previous_edge_ids[dynamic_edge[1]]][0]
    elif dynamic_edge[0] == 5:
        previous_edge_ids:Array = list(layer_map.beveled_leftright_edges_to_last_edge.keys())
        edge_ids = layer_map.beveled_leftright_edges_to_last_edge[previous_edge_ids[dynamic_edge[1]]][1]
    return edge_ids

class SIMPLE_MORPH_219_REAL_CORNER_OPERATIONS( Operator ):
    bl_idname = 'simplemorph.219_real_corner_operations_op'
    bl_label = 'Real Corner 219 - Layer Settings'
    bl_description = 'Simplemorph_219_op_description'
    bl_options = { 'REGISTER', 'UNDO' }

    real_corner_layer_name: StringProperty()
    real_corner_layer_index: IntProperty()

    originalObjectName: StringProperty()
    placeholderObjectName: StringProperty()
    objectLayerBeingModified: StringProperty()

    action: EnumProperty(
        items = [
            ( "DO_NOTHING", "Do Nothing", "Does absolutely nothing" ),
            ( "ADD_BEVEL_LAYER", "Add Bevel Layer", "Adds a new bevel layer to the mesh" ),
            ( "MARK_AS_219_BASE", "Mark As 219 Base", "Marks the current object as a base object for all Simple Morph operations." ),
            ( "UPDATE_LAYER", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" ),
            ( "CAPTURE_OPERATION", "CAPTURE OPERATION", "Initiates the operator menu for setting the bevel layer's settings" ),
        ]
    )
    
    affect: EnumProperty(
        name = 'Affect',
        description = 'Affect edges or vertices',
        default = 'EDGES',
        items = [
            ('VERTICES', 'Vertices', 'Affect only vertices'),
            ('EDGES', 'Edges', 'Affect only edges')
        ],
        update = update_real_corner_bevel_values
	)
    
    offset_type: EnumProperty(
        name = 'Width Type',
        description = 'The method for determining the size of the bevel',
        default = 'OFFSET',
        items = [
            ('OFFSET', 'Offset', 'Amount is offset of new edges from original'),
            ('WIDTH', 'Width', 'Amount is width of new face'),
            ('DEPTH', 'Depth', 'Amount is perpendicular distance from original edge to bevel face'),
            ('PERCENT', 'Percent', 'Amount is percent of adjacent edge length'),
            ('ABSOLUTE', 'Absolute', 'Amount is absolute distance along adjacent edge')
        ],
        update = update_real_corner_bevel_values
    )
    
    offset: FloatProperty(
        name = 'Width',
        description = 'Bevel amount',
        default = 0.0,
        soft_min = 0.0,
        soft_max = 100.0,
        precision = 3,
        update = update_real_corner_bevel_values
	)
    
    offset_pct: FloatProperty(
        name = 'Width Percent',
        description = 'Bevel amount for percentage method',
        default = 0.0,
        soft_min = 0.0,
        soft_max = 100.0,
        precision = 3,
        update = update_real_corner_bevel_values
	)
    
    segments: IntProperty(
        name = 'Segments',
        description = 'Segments for curved edge',
        default = 1,
        soft_min = 1,
        soft_max = 100,
        update = update_real_corner_bevel_values
	)
    
    profile: FloatProperty(
        name = 'Profile',
        description = 'Controls profile shape (0.5 = round)',
        default = 0.5,
        soft_min = 0.0,
        soft_max = 1.0,
        precision = 3,
        update = update_real_corner_bevel_values
	)
    
    material: IntProperty(
        name = 'Material Index',
        description = 'Material for bevel faces (-1 means use adjacent faces)',
        default = -1,
        soft_min = -1,
        soft_max = 100,
        update = update_real_corner_bevel_values
	)
    
    harden_normals: BoolProperty(
        name = 'Harden Normals',
        description = 'Match normals of new faces to adjacent faces',
        default = False,
        update = update_real_corner_bevel_values
	)
    
    clamp_overlap: BoolProperty(
        name = 'Clamp Overlap',
        description = 'Do not allow beveled edges/vertices to overlap each other',
        default = False,
        update = update_real_corner_bevel_values
	)
    
    loop_slide: BoolProperty(
        name = 'Loop Slide',
        description = 'Prefer sliding along edges to even widths',
        default = True,
        update = update_real_corner_bevel_values
	)
    
    mark_seam: BoolProperty(
        name = 'Mark Seams',
        description = 'Mark Seams along beveled edges',
        default = False,
        update = update_real_corner_bevel_values
	)
    
    mark_sharp: BoolProperty(
        name = 'Mark Sharp',
        description = 'Mark beveled edges as sharp',
        default = False,
        update = update_real_corner_bevel_values
	)
    
    miter_outer: EnumProperty(
        name = 'Outer Miter',
        description = 'Pattern to use for outside of miters',
        default = 'SHARP',
        items = [
            ('SHARP', 'Sharp', 'Outside of miter is sharp'),
            ('PATCH', 'Patch', 'Outside of miter is squared-off patch'),
            ('ARC', 'Arc', 'Outside of miter is arc')
        ],
        update = update_real_corner_bevel_values
	)
    
    miter_inner: EnumProperty(
        name = 'Inner Miter',
        description = 'Pattern to use for inside of miters',
        default = 'SHARP',
        items = [
            ('SHARP', 'Sharp', 'Inside of miter is sharp'),
            ('ARC', 'Arc', 'Inside of miter is arc')
        ],
        update = update_real_corner_bevel_values
	)
    
    spread: FloatProperty(
        name = 'Spread',
        description = 'Amount to spread arcs for arc inner miters',
        default = 0.1,
        soft_min = 0.0,
        soft_max = 100.0,
        precision = 3,
        update = update_real_corner_bevel_values
	)
    
    vmesh_method: EnumProperty(
        name = 'Vertex Mesh Method',
        description = 'The method to use to create meshes at intersections',
        default = 'ADJ',
        items = [
            ('ADJ', 'Grid Fill', 'Default patterned fill'),
            ('CUTOFF', 'Cutoff', "A cutoff at each profile's end before the intersection")
        ],
        update = update_real_corner_bevel_values
	)
    
    face_strength_mode: EnumProperty(
        name = 'Face Strength Mode',
        description = 'Whether to set face strength, and which faces to set face strength on',
        default = 'NONE',
        items = [
            ('NONE', 'None', 'Do not set face strength'),
            ('NEW', 'New', 'Set face strength on new faces only'),
            ('AFFECTED', 'Affected', 'Set face strength on new and modified faces only'),
            ('ALL', 'All', 'Set face strength on all faces')
        ],
        update = update_real_corner_bevel_values
	)
    
    profile_type: EnumProperty(
        name = 'Profile Type',
        description = 'The type of shape used to rebuild a beveled section',
        default = 'SUPERELLIPSE',
        items = [
            ('SUPERELLIPSE', 'Superellipse', 'The profile can be a concave or convex curve'),
            ('CUSTOM', 'Custom', 'The profile can be any arbitrary path between its endpoints')
        ],
        update = update_real_corner_bevel_values
    )
    
    def draw( self, context ):
        pass

    def execute( self, context ):
        global realCorner219CurrentState, realCorner219SelectedBaseObjName, realCorner219ModifiedObjName, realcorner219HandleSelectDeselectFunctionLocked, update_real_corner_bevel_values_locked
        
        selectedObject = bpy.context.selected_objects
        
        if len( selectedObject ) == 0:
            return { 'CANCELLED' }
        
        selectedObject = selectedObject[0]
        
        if self.action == 'ADD_BEVEL_LAYER':
            createNewCustomProperty(bpy.data.objects[ self.originalObjectName ], realCorner219PropName, 'bevel')
            return { 'CANCELLED' }
        elif self.action == 'MARK_AS_219_BASE':
            simplemorph219.markObjectAsSimpleMorphBaseObject( bpy.data.objects[ self.originalObjectName ] )
            return { 'CANCELLED' }
        elif self.action == 'UPDATE_LAYER':
            realcorner219HandleSelectDeselectFunctionLocked = True
            realCorner219CurrentState = realCorner219States.UPDATING_LAYER
            realCorner219SelectedBaseObjName = selectedObject.name
            salowell_bpy_lib.isolate_object_select( selectedObject )
            
            bpy.ops.object.mode_set( mode = 'OBJECT')
            bpy.ops.object.duplicate()
            bpy.data.objects[ self.originalObjectName ].hide_viewport = True
            updatedObject = context.selected_objects[0]
            updatedObject[ simplemorph219.simpleMorph219BaseName ] = False
            salowell_bpy_lib.isolate_object_select( updatedObject )
            realCorner219ModifiedObjName = updatedObject.name
            self.placeholderObjectName = context.selected_objects[0].name
            
            gen_real_corner_meshes_result:Array = gen_real_corner_meshes(updatedObject, self.real_corner_layer_name)
            real_corner_meshes:Array = gen_real_corner_meshes_result[0]
            real_corner_layer_maps:Array = gen_real_corner_meshes_result[7]
            
            bpy.ops.object.mode_set( mode = 'OBJECT')
            context.selected_objects[0].update_from_editmode()
            realcorner219HandleSelectDeselectFunctionLocked = False
            
            layer_index:int = int(self.real_corner_layer_name.split('_')[1]) - 1
            layer_properties:dict = realCornerPropIndexToDict(context.selected_objects[0], context.scene.realCorner219Layers)
            bpy.ops.object.mode_set( mode = 'EDIT')
            mesh = bpy.context.object.data
            bpy.ops.mesh.select_all(action='DESELECT')
            
            if layer_index < 0:
                bm = bmesh.new()
                bm.from_mesh(mesh)
            else:
                bm = real_corner_meshes[len(real_corner_meshes) - 2]
            
            bm.edges.ensure_lookup_table()
            
            edges_to_select:Array = []
            
            if len(layer_properties['edge_references']) != 0:
                for edge_reference in layer_properties['edge_references']:
                    edges = get_edges_from_dynamic_edge_fast(edge_reference, real_corner_layer_maps[edge_reference[3]])
                    
                    for edge_id in edges:
                        edges_to_select.append(edge_id)
            else:
                edges_to_select = layer_properties['edges']
            
            for edge_id in edges_to_select:
                bm.edges[edge_id].select = True
            
            bpy.ops.object.mode_set( mode = 'OBJECT')
            bm.to_mesh(mesh)
            bpy.ops.object.mode_set( mode = 'EDIT')
            
            bpy.ops.mesh.bevel(
                'INVOKE_DEFAULT',
                offset_type = salowell_bpy_lib.bevel_offset_type_items(layer_properties['bevel_settings']['offset_type']).name,
                offset = float(layer_properties['bevel_settings']['offset']),
                profile_type = salowell_bpy_lib.bevel_profile_type_items(layer_properties['bevel_settings']['profile_type']).name,
                offset_pct = float(layer_properties['bevel_settings']['offset_pct']),
                segments = int(layer_properties['bevel_settings']['segments']),
                profile = float(layer_properties['bevel_settings']['profile']),
                affect = salowell_bpy_lib.bevel_affect_items(layer_properties['bevel_settings']['affect']).name,
                clamp_overlap = bool(int(layer_properties['bevel_settings']['clamp_overlap'])),
                loop_slide = bool(int(layer_properties['bevel_settings']['loop_slide'])),
                mark_seam = bool(int(layer_properties['bevel_settings']['mark_seam'])),
                mark_sharp = bool(int(layer_properties['bevel_settings']['mark_sharp'])),
                material = int(layer_properties['bevel_settings']['material']),
                harden_normals = bool(int(layer_properties['bevel_settings']['harden_normals'])),
                face_strength_mode = salowell_bpy_lib.bevel_face_strength_mode_items(layer_properties['bevel_settings']['face_strength_mode']).name, 
                miter_outer = salowell_bpy_lib.bevel_miter_outer_items(layer_properties['bevel_settings']['miter_outer']).name, 
                miter_inner = salowell_bpy_lib.bevel_miter_inner_items(layer_properties['bevel_settings']['miter_inner']).name, 
                spread = float(layer_properties['bevel_settings']['spread']),
                vmesh_method = salowell_bpy_lib.bevel_vmesh_method_items(layer_properties['bevel_settings']['vmesh_method']).name, 
                release_confirm = False
            )
        elif self.action == 'CAPTURE_OPERATION':
            layer_properties:dict = realCornerPropIndexToDict(context.selected_objects[0], context.scene.realCorner219Layers)
            
            active_op = bpy.context.active_operator
            
            if active_op:
                if active_op.bl_idname == 'MESH_OT_bevel':
                    if hasattr(active_op, "properties"):
                        layer_properties['bevel_settings']['affect'] = salowell_bpy_lib.bevel_affect_items[active_op.properties.affect].value
                        layer_properties['bevel_settings']['offset_type'] = salowell_bpy_lib.bevel_offset_type_items[active_op.properties.offset_type].value
                        layer_properties['bevel_settings']['offset'] = active_op.properties.offset
                        layer_properties['bevel_settings']['offset_pct'] = active_op.properties.offset_pct
                        layer_properties['bevel_settings']['segments'] = active_op.properties.segments
                        layer_properties['bevel_settings']['profile'] = active_op.properties.profile
                        layer_properties['bevel_settings']['material'] = active_op.properties.material
                        layer_properties['bevel_settings']['harden_normals'] = bool(active_op.properties.harden_normals)
                        layer_properties['bevel_settings']['clamp_overlap'] = bool(active_op.properties.clamp_overlap)
                        layer_properties['bevel_settings']['loop_slide'] = bool(active_op.properties.loop_slide)
                        layer_properties['bevel_settings']['mark_seam'] = bool(active_op.properties.mark_seam)
                        layer_properties['bevel_settings']['mark_sharp'] = bool(active_op.properties.mark_sharp)
                        layer_properties['bevel_settings']['miter_outer'] = salowell_bpy_lib.bevel_miter_outer_items[active_op.properties.miter_outer].value
                        layer_properties['bevel_settings']['miter_inner'] = salowell_bpy_lib.bevel_miter_inner_items[active_op.properties.miter_inner].value
                        layer_properties['bevel_settings']['spread'] = active_op.properties.spread
                        layer_properties['bevel_settings']['vmesh_method'] = salowell_bpy_lib.bevel_vmesh_method_items[active_op.properties.vmesh_method].value
                        layer_properties['bevel_settings']['face_strength_mode'] = salowell_bpy_lib.bevel_face_strength_mode_items[active_op.properties.face_strength_mode].value
                        layer_properties['bevel_settings']['profile_type'] = salowell_bpy_lib.bevel_profile_type_items[active_op.properties.profile_type].value
                        layer_properties_string:str = realCornerPropDictToStringBevel(layer_properties)
                        
                        bpy.data.objects.get(realCorner219SelectedBaseObjName)[context.scene.realCorner219Layers] = layer_properties_string
        else:
            realcorner219HandleSelectDeselectFunctionLocked = True
            update_real_corner_bevel_values_locked = True
            
            bpy.ops.object.mode_set( mode = 'OBJECT')
            
            if selectedObject.name != self.originalObjectName:
                bpy.ops.object.delete()
                
            bpy.data.objects[ self.originalObjectName ].hide_viewport = False
            salowell_bpy_lib.isolate_object_select( bpy.data.objects[ self.originalObjectName ] )
            bpy.ops.object.duplicate()
            bpy.data.objects[ self.originalObjectName ].hide_viewport = True
            updatedObject = context.selected_objects[0]
            updatedObject[ simplemorph219.simpleMorph219BaseName ] = False
            salowell_bpy_lib.isolate_object_select( updatedObject )
            
            real_corner_meshes:Array = gen_real_corner_meshes( updatedObject, self.real_corner_layer_name )[0]
            self.placeholderObjectName = context.selected_objects[0].name
            
            bpy.ops.object.mode_set( mode = 'OBJECT')
            real_corner_meshes[-1].to_mesh(context.selected_objects[0].data)
            context.selected_objects[0].update_from_editmode() 
            
            realcorner219HandleSelectDeselectFunctionLocked = False
            update_real_corner_bevel_values_locked = False
        self.action = 'DO_NOTHING'
        
        return { 'FINISHED' }

class SIMPLE_MORPH_219_REAL_CORNER_PT_panel( Panel ):
    bl_idname = 'SIMPLE_MORPH_219_REAL_CORNER_PT_panel'
    bl_label = 'Real Corner 219'
    bl_description = 'Simplemorph_219_op_description'
    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    
    originalObjectName:str = ''
    placeholderObjectName:str = ''
 
    action: EnumProperty(
        items = [
            ( 'BEVEL_MANAGER', 'align x +', 'align x +' ),
        ]
    )

    def draw( self, context ):
        global realCorner219CurrentState, realCorner219SelectedBaseObjName, realCorner219ModifiedObjName
        
        selectedObject = None
        hasLayers:bool = len ( update_real_corner_selection_list( bpy.types.Scene, context ) ) != 0
        
        layout = self.layout
        
        testQuickBtn = layout.column()
        testQuickObj = testQuickBtn.operator( 'realcorner219.real_corner_quickops_op', text = 'Test Quick' )
        testQuickObj.action = 'TEST_QUICK'
        
        if context.selected_objects is not None and len( context.selected_objects ) > 0:
            selectedObject = context.selected_objects[0]
        
        realCorner219LayerIndex = ''
        
        if simplemorph219.isSimpleMorphBaseObject( selectedObject ):
            createLayerBtn = layout.column()
            createBevelLayerObj = createLayerBtn.operator( 'simplemorph.219_real_corner_operations_op', text = 'Add Bevel Layer' )
            createBevelLayerObj.action = 'ADD_BEVEL_LAYER'
            createBevelLayerObj.originalObjectName = selectedObject.name
        
        if simplemorph219.isSimpleMorphBaseObject( selectedObject ) and selectedObject is not None and realCorner219CurrentState == realCorner219States.NONE:
            turnOnEditModeBtn = layout.column()
            turnOnEditModeObj = turnOnEditModeBtn.operator( 'realcorner219.real_corner_quickops_op', text = 'Turn On Select Mode' )
            turnOnEditModeObj.action = 'TURN_ON_SELECT_MODE'
        elif ( simplemorph219.isSimpleMorphBaseObject( selectedObject ) or simplemorph219.isSimpleMorphTempBaseObject( selectedObject ) ) and selectedObject is not None and realCorner219CurrentState == realCorner219States.SELECTING_EDGE:
            turnOffEditModeBtn = layout.column()
            turnOffEditModeObj = turnOffEditModeBtn.operator( 'realcorner219.real_corner_quickops_op', text = 'Save and Turn Off Select Mode' )
            turnOffEditModeObj.action = 'TURN_OFF_AND_SAVE_SELECT_MODE'
        
        if not simplemorph219.isSimpleMorphBaseObject( selectedObject ) and selectedObject is not None:
            markAsBaseBtn = layout.column()
            markAsBaseObj = markAsBaseBtn.operator( 'simplemorph.219_real_corner_operations_op', text = 'Mark As 219 Base' )
            
            if simplemorph219.isSimpleMorphTempBaseObject( selectedObject ):
                markAsBaseBtn.enabled = False
            
            markAsBaseObj.action = 'MARK_AS_219_BASE'
            markAsBaseObj.originalObjectName = selectedObject.name
        
        if hasLayers:
            layout.prop(context.scene, "realCorner219Layers")
            realCorner219LayerIndex = context.scene.realCorner219Layers
        
        if hasLayers:
            updateLayerBtn = layout.column()
            captureOperationBtn = layout.column()
            updateLayerObj = updateLayerBtn.operator( 'simplemorph.219_real_corner_operations_op', text = 'Update Layer' )
            captureOperationObj = captureOperationBtn.operator('simplemorph.219_real_corner_operations_op', text = 'Capture Operation')
            
            if not simplemorph219.isSimpleMorphBaseObject( selectedObject ):
                updateLayerBtn.enabled = False
            else:
                captureOperationBtn.enabled = False
            
            updateLayerObj.action = 'UPDATE_LAYER'
            updateLayerObj.real_corner_layer_name = realCorner219LayerIndex
            updateLayerObj.real_corner_layer_index = get_real_corner_custom_prop_key_index( context.selected_objects[0], realCorner219LayerIndex )
            updateLayerObj.originalObjectName = selectedObject.name
            updateLayerObj.objectLayerBeingModified = context.scene.realCorner219Layers
            
            captureOperationObj.action = 'CAPTURE_OPERATION'
            captureOperationObj.real_corner_layer_name = realCorner219LayerIndex
            captureOperationObj.real_corner_layer_index = get_real_corner_custom_prop_key_index(context.selected_objects[0], realCorner219LayerIndex)
            
            captureOperationObj.originalObjectName = realCorner219SelectedBaseObjName
            
            captureOperationObj.objectLayerBeingModified = context.scene.realCorner219Layers
    
    def execute( self, context ):
        bevelLayers = get_all_real_corner_custom_prop_keys( context.selected_objects[0] )

        if len( bevelLayers ) == 0:
            keyName = createNewCustomProperty(context.selected_objects[0], realCorner219PropName, 'bevel')
            bevelLayers.append( keyName )
        
        bevelSegments=3
        
        me = bpy.context.active_object.data
        bm:bmesh = bmesh.new()
        bm.from_mesh( me )
        
        iniSelEdgeObjs = salowell_bpy_lib.getBmeshSelectedEdges( bm )[0]
        
        #bm.edges.ensure_lookup_table()
        #bm.faces.ensure_lookup_table()
        #What is smoothresh and custom_profile? These aren't present in the bpy.ops.mesh version of bevel. https://docs.blender.org/api/current/bmesh.ops.html#bmesh.ops.bevel
        #offset_pct and release_confirm are not present in the Bmesh version of bevel. https://docs.blender.org/api/current/bpy.ops.mesh.html#bpy.ops.mesh.bevel
        #Removed "custom_profile = None" as it currently throws an error [NotImplementedError: bevel: keyword "custom_profile" type 4 not working yet!]
        newData:dict = bmesh.ops.bevel( bm, geom = iniSelEdgeObjs, offset = 0.02, offset_type = 'WIDTH', profile_type = 'SUPERELLIPSE', segments = bevelSegments, profile = 0.5, affect = 'EDGES', clamp_overlap = False, material = -1, loop_slide = True, mark_seam = False, mark_sharp = False, harden_normals = False, face_strength_mode = 'NONE', miter_outer = 'SHARP', miter_inner = 'SHARP', spread = 0.1, smoothresh = 0, vmesh_method = 'ADJ' )
        
        bpy.ops.mesh.select_mode( type = 'FACE' )
        
        edgeFaces = []
        faceIndex = 0
        
        for face in newData[ 'faces' ]:
            edgeIndex = int( faceIndex / bevelSegments )
            
            if edgeIndex >= len( edgeFaces ):
                edgeFaces.append( [] )
            
            edgeFaces[ edgeIndex ].append( face )
            faceIndex += 1
        
        bpy.ops.object.mode_set( mode = 'OBJECT')
        bm.to_mesh( me )
        bpy.ops.object.mode_set( mode = 'EDIT')
    
    @staticmethod
    def align_controller( context , direction ):
        pass

def selectedEdgesToCustomPropArray( obj ):
    return salowell_bpy_lib.get_selected_edges( obj )[1]

def createEmptyRealCornerPropDict(propertyType:str) -> dict:
    propertyType = propertyType.lower()
    realCornerPropDict:dict = {}
    realCornerPropDict['vertices'] = []
    realCornerPropDict[ 'edges' ] = []
    realCornerPropDict['faces'] = []
    
    #[0] = The type of dynamic edge [0 = Unbeveled, 1 = beveled start, 2 = beveled end, 3 = beveled parallel, 4 = beveled left, 5 = beveled right]
    #[1] = The index within the object type[beveled_faces_to_last_edge, beveled_startend_edges_to_last_edge, etc...] this selection is.
    #[2] = Only used for certain object types such as parallel edges (These edges will change in number depending on LOD, thus, this value represents a percentage of  which edge within the parallel edges this selection belongs to)
    #[3] = Which layer map this points back to. Sometimes you may select a leftright edge that was created several layers ago and the object needs a way to know how far back the selection is mapped.
    if propertyType == 'bevel':
        realCornerPropDict[ 'edge_references' ] = []
        realCornerPropDict[ 'bevel_settings' ] = {}
        realCornerPropDict[ 'bevel_settings' ][ 'affect' ]:int = 1
        realCornerPropDict[ 'bevel_settings' ][ 'offset_type' ]:int = 0
        realCornerPropDict[ 'bevel_settings' ][ 'offset' ]:float = 0.0
        realCornerPropDict[ 'bevel_settings' ][ 'offset_pct' ]:float = 0.0
        realCornerPropDict[ 'bevel_settings' ][ 'segments' ]:int = 1
        realCornerPropDict[ 'bevel_settings' ][ 'profile' ]:float = 0.5
        realCornerPropDict[ 'bevel_settings' ][ 'material' ]:int = -1
        realCornerPropDict[ 'bevel_settings' ][ 'harden_normals' ]:bool = False
        realCornerPropDict[ 'bevel_settings' ][ 'clamp_overlap' ]:bool = False
        realCornerPropDict[ 'bevel_settings' ][ 'loop_slide' ]:bool = True
        realCornerPropDict[ 'bevel_settings' ][ 'mark_seam' ]:bool = False
        realCornerPropDict[ 'bevel_settings' ][ 'mark_sharp' ]:bool = False
        realCornerPropDict[ 'bevel_settings' ][ 'miter_outer' ]:int = 0
        realCornerPropDict[ 'bevel_settings' ][ 'miter_inner' ]:int = 0
        realCornerPropDict[ 'bevel_settings' ][ 'spread' ]:float = 0.1
        realCornerPropDict[ 'bevel_settings' ][ 'vmesh_method' ]:int = 0
        realCornerPropDict[ 'bevel_settings' ][ 'face_strength_mode' ]:int = 0
        realCornerPropDict[ 'bevel_settings' ][ 'profile_type' ]:int = 0
    
    return realCornerPropDict

def realCornerPropDictToStringBevel( realCornerPropDict:dict ) -> str:
    affect:str = str( realCornerPropDict[ 'bevel_settings' ][ 'affect' ] )
    offset_type:str = str( realCornerPropDict[ 'bevel_settings' ][ 'offset_type' ] )
    offset:str = str( realCornerPropDict[ 'bevel_settings' ][ 'offset' ] )
    offset_pct:str = str( realCornerPropDict[ 'bevel_settings' ][ 'offset_pct' ] )
    segments:str = str( realCornerPropDict[ 'bevel_settings' ][ 'segments' ] )
    profile:str = str( realCornerPropDict[ 'bevel_settings' ][ 'profile' ] )
    material:str = str( realCornerPropDict[ 'bevel_settings' ][ 'material' ] )
    harden_normals:str = str( int( realCornerPropDict[ 'bevel_settings' ][ 'harden_normals' ] ) )
    clamp_overlap:str = str( int( realCornerPropDict[ 'bevel_settings' ][ 'clamp_overlap' ] ) )
    loop_slide:str = str( int( realCornerPropDict[ 'bevel_settings' ][ 'loop_slide' ] ) )
    mark_seam:str = str( int( realCornerPropDict[ 'bevel_settings' ][ 'mark_seam' ] ) )
    mark_sharp:str = str( int( realCornerPropDict[ 'bevel_settings' ][ 'mark_sharp' ] ) )
    miter_outer:str = str( realCornerPropDict[ 'bevel_settings' ][ 'miter_outer' ] )
    miter_inner:str = str( realCornerPropDict[ 'bevel_settings' ][ 'miter_inner' ] )
    spread:str = str( realCornerPropDict[ 'bevel_settings' ][ 'spread' ] )
    vmesh_method:str = str( realCornerPropDict[ 'bevel_settings' ][ 'vmesh_method' ] )
    face_strength_mode:str = str( realCornerPropDict[ 'bevel_settings' ][ 'face_strength_mode' ] )
    profile_type:str = str( realCornerPropDict[ 'bevel_settings' ][ 'profile_type' ] )
    
    realCornerPropString:str = '219:0(' + ','.join( str( edgeId ) for edgeId in realCornerPropDict[ 'edges' ] ) + ')'
    realCornerPropString = realCornerPropString + '(' + affect + ',' + offset_type + ',' + offset + ',' + offset_pct + ',' + segments + ',' + profile + ',' + material + ',' + harden_normals + ',' + clamp_overlap + ',' + loop_slide + ',' + mark_seam + ',' + mark_sharp + ',' + miter_outer + ',' + miter_inner + ',' + spread + ',' + vmesh_method + ',' + face_strength_mode + ',' + profile_type + ')'
    
    realCornerPropString = realCornerPropString + '(' + ','.join( str( edge_reference[0] ) + ':' + str( edge_reference[1] ) + ':' + str( edge_reference[2] ) + ':' + str( edge_reference[3] ) for edge_reference in realCornerPropDict[ 'edge_references' ] ) + ')'
    
    return realCornerPropString

def realCornerPropIndexToDict( obj:object, propKey:str ) -> dict:
    if obj[propKey].strip().startswith('219:0'):
        return realCornerBevelPropStringToDict(obj[propKey])

def realCornerBevelPropStringToDict( realCornerPropString:str ) -> str:
    realCornerPropDict = createEmptyRealCornerPropDict('bevel')
    
    propertyValues = realCornerPropString.strip().lstrip( '219:0' ).lstrip( '(' ).rstrip( ')' ).split( ')(' )
    
    for index, value in enumerate( propertyValues ):
        split = value.split( ',' )
        
        if index == 0 and value != '':
            for edgeIndex, edgeValue in enumerate( split ):
                if edgeValue != '':
                    split[ edgeIndex ] = int( edgeValue )
            
            realCornerPropDict[ 'edges' ] = split
        elif index == 1 and value != '':
            split_length = len( split )
            
            realCornerPropDict[ 'bevel_settings' ][ 'affect' ] = realCornerPropDict[ 'bevel_settings' ][ 'affect' ] if split_length < 1 else int( split[0] )
            realCornerPropDict[ 'bevel_settings' ][ 'offset_type' ] = realCornerPropDict[ 'bevel_settings' ][ 'offset_type' ] if split_length < 2 else int( split[1] )
            realCornerPropDict[ 'bevel_settings' ][ 'offset' ] = realCornerPropDict[ 'bevel_settings' ][ 'offset' ] if split_length < 3 else float( split[2] )
            realCornerPropDict[ 'bevel_settings' ][ 'offset_pct' ] = realCornerPropDict[ 'bevel_settings' ][ 'offset_pct' ] if split_length < 4 else float( split[3] )
            realCornerPropDict[ 'bevel_settings' ][ 'segments' ] = realCornerPropDict[ 'bevel_settings' ][ 'segments' ] if split_length < 5 else int( split[4] )
            realCornerPropDict[ 'bevel_settings' ][ 'profile' ] = realCornerPropDict[ 'bevel_settings' ][ 'profile' ] if split_length < 6 else float( split[5] )
            realCornerPropDict[ 'bevel_settings' ][ 'material' ] = realCornerPropDict[ 'bevel_settings' ][ 'material' ] if split_length < 7 else int( split[6] )
            realCornerPropDict[ 'bevel_settings' ][ 'harden_normals' ] = realCornerPropDict[ 'bevel_settings' ][ 'harden_normals' ] if split_length < 8 else bool( int( split[7] ) )
            realCornerPropDict[ 'bevel_settings' ][ 'clamp_overlap' ] = realCornerPropDict[ 'bevel_settings' ][ 'clamp_overlap' ] if split_length < 9 else bool( int( split[8] ) )
            realCornerPropDict[ 'bevel_settings' ][ 'loop_slide' ] = realCornerPropDict[ 'bevel_settings' ][ 'loop_slide' ] if split_length < 10 else bool( int( split[9] ) )
            realCornerPropDict[ 'bevel_settings' ][ 'mark_seam' ] = realCornerPropDict[ 'bevel_settings' ][ 'mark_seam' ] if split_length < 11 else bool( int( split[10] ) )
            realCornerPropDict[ 'bevel_settings' ][ 'mark_sharp' ] = realCornerPropDict[ 'bevel_settings' ][ 'mark_sharp' ] if split_length < 12 else bool( int( split[11] ) )
            realCornerPropDict[ 'bevel_settings' ][ 'miter_outer' ] = realCornerPropDict[ 'bevel_settings' ][ 'miter_outer' ] if split_length < 13 else int( split[12] )
            realCornerPropDict[ 'bevel_settings' ][ 'miter_inner' ] = realCornerPropDict[ 'bevel_settings' ][ 'miter_inner' ] if split_length < 14 else int( split[13] )
            realCornerPropDict[ 'bevel_settings' ][ 'spread' ] = realCornerPropDict[ 'bevel_settings' ][ 'spread' ] if split_length < 15 else float( split[14] )
            realCornerPropDict[ 'bevel_settings' ][ 'vmesh_method' ] = realCornerPropDict[ 'bevel_settings' ][ 'vmesh_method' ] if split_length < 16 else int( split[15] )
            realCornerPropDict[ 'bevel_settings' ][ 'face_strength_mode' ] = realCornerPropDict[ 'bevel_settings' ][ 'face_strength_mode' ] if split_length < 17 else int( split[16] )
            realCornerPropDict[ 'bevel_settings' ][ 'profile_type' ] = realCornerPropDict[ 'bevel_settings' ][ 'profile_type' ] if split_length < 18 else int( split[17] )
        elif index == 2 and value != '':
            for edgeIndex, edgeValue in enumerate( split ):
                if edgeValue != '':
                    edgeValue = edgeValue.split(':')
                    
                    edgeValue[0] = int(edgeValue[0])
                    edgeValue[1] = int(edgeValue[1])
                    edgeValue[2] = float(edgeValue[2])
                    edgeValue[3] = int(edgeValue[3])
                    
                    split[ edgeIndex ] = edgeValue
            
            realCornerPropDict[ 'edge_references' ] = split
    
    return realCornerPropDict

#This is currently a hacky solution for updating. I need to learn the correct design paradigm for Blender's API.
@bpy.app.handlers.persistent
def applyRealCornerUpdate( scene ) -> None:
    global realCorner219LastUpdate
    
    if len( realCorner219LastUpdate ) != 0:
        bpy.data.objects[ realCorner219LastUpdate[0] ][ realCorner219LastUpdate[1] ] = realCorner219LastUpdate[2]
        realCorner219LastUpdate = []

def genRealCornerMeshAtPrevIndex( obj, layerIndexKey ) -> Array | Array | Array:
    propKeyIndex = get_real_corner_custom_prop_key_index( obj, layerIndexKey )
    generated_meshes:Array = []
    selected_face_objects:Array = []
    selected_face_indexes:Array = []
    selected_edge_objects:Array = []
    selected_edge_indexes:Array = []
    selected_vertex_objects:Array = []
    selected_vertices:Array = []
    
    if propKeyIndex > 0:
        propKeyIndex -= 1
        PropKeysArr = get_all_real_corner_custom_prop_keys( obj )
        generated_meshes, selected_face_objects, selected_face_indexes, selected_edge_objects, selected_edge_indexes, selected_vertex_objects, selected_vertices, layer_maps =  gen_real_corner_meshes( obj, PropKeysArr[ propKeyIndex ] )

    return generated_meshes, selected_face_objects, selected_face_indexes, selected_edge_objects, selected_edge_indexes, selected_vertex_objects, selected_vertices

def gen_real_corner_meshes_from_index( obj:object, index:int ) -> Array | Array | Array | Array | Array | Array | Array:
    if index == -1:
        generated_meshes:Array = []
        generated_meshes.append( salowell_bpy_lib.mesh_to_bmesh( obj.data ) )
        selected_face_objects:Array = []
        selected_face_indexes:Array = []
        selected_edge_objects:Array = []
        selected_edge_indexes:Array = []
        selected_vertex_objects:Array = []
        selected_vertices:Array = []
        
        return generated_meshes, selected_face_objects, selected_face_indexes, selected_edge_objects, selected_edge_indexes, selected_vertex_objects, selected_vertices
    elif index < -1:
        index += 1
    
    real_corner_layer_prop_keys:Array = get_all_real_corner_custom_prop_keys( obj )
    
    prop_key:str = real_corner_layer_prop_keys[ index ]
    
    return gen_real_corner_meshes( obj, prop_key )
    
def gen_real_corner_meshes( obj:object, layerIndexKey:str ) -> Array | Array | Array | Array | Array | Array | Array | Array:
    global simple_morph_219_object_list, realCorner219SelectedBaseObjName, realCorner219ModifiedObjName
    
    simple_morph_219_obj:simple_morph_219_object = create_if_not_exists_simple_morph_219_object(obj.name)
    blender_mesh:bmesh.types.BMesh = salowell_bpy_lib.mesh_to_bmesh(obj.data)
    
    selected_face_objects:Array = []
    selected_face_indexes:Array = []
    selected_edge_objects:Array = []
    selected_edge_indexes:Array = []
    selected_vertex_objects:Array = []
    selected_vertices:Array = []
    generated_meshes:Array = []
    
    realCornerPropKeys = get_all_real_corner_custom_prop_keys( obj )
    layerIndex = get_real_corner_custom_prop_key_index( obj, layerIndexKey )
    
    previous_blender_mesh:bmesh.types.BMesh = None
    layer_map:simple_morph_219_object = None
    layer_maps:Array = []
    
    for propKey in range( 0, layerIndex + 1 ):
        if propKey == 0:
            previous_blender_mesh = salowell_bpy_lib.mesh_to_bmesh(obj.data)
        
        propDic = realCornerPropIndexToDict( obj, realCornerPropKeys[ propKey ] )
        
        grouped_faces = salowell_bpy_lib.separate_orphaned_and_faced_edges(blender_mesh, propDic[ 'edges' ])
        
        edge_selection_type = 0
        
        if len(grouped_faces[1]) > 0:
            edge_selection_type = 1
        
        edges_to_bevel:Array = propDic[ 'edges' ]
        
        if len( propDic[ 'edge_references' ] ) > 0 and simple_morph_219_obj is not None and propKey > 0:
            previous_layer_key = get_previous_real_corner_custom_prop_key(bpy.data.objects[simple_morph_219_obj.object_name], realCornerPropKeys[ propKey ])
            edges_to_bevel = []
            
            for edge_prop in propDic[ 'edge_references' ]:
                edges_to_bevel = edges_to_bevel + edge_reference_to_edges(edge_prop, simple_morph_219_obj, previous_layer_key)
        
        bevel_result = salowell_bpy_lib.bevel(
            blender_mesh = blender_mesh,
            edge_ids_to_bevel = edges_to_bevel,
            offset_type = salowell_bpy_lib.bevel_offset_type_items( propDic[ 'bevel_settings' ][ 'offset_type' ] ).name, 
            offset = propDic[ 'bevel_settings' ][ 'offset' ], 
            profile_type = salowell_bpy_lib.bevel_profile_type_items( propDic[ 'bevel_settings' ][ 'profile_type' ] ).name, 
            offset_pct = propDic[ 'bevel_settings' ][ 'offset_pct' ], 
            segments = propDic[ 'bevel_settings' ][ 'segments' ], 
            profile = propDic[ 'bevel_settings' ][ 'profile' ], 
            affect = salowell_bpy_lib.bevel_affect_items( propDic[ 'bevel_settings' ][ 'affect' ] ).name,
            clamp_overlap = propDic[ 'bevel_settings' ][ 'clamp_overlap' ], 
            loop_slide = propDic[ 'bevel_settings' ][ 'loop_slide' ], 
            mark_seam = propDic[ 'bevel_settings' ][ 'mark_seam' ], 
            mark_sharp = propDic[ 'bevel_settings' ][ 'mark_sharp' ], 
            material = propDic[ 'bevel_settings' ][ 'material' ], 
            harden_normals = propDic[ 'bevel_settings' ][ 'harden_normals' ], 
            face_strength_mode = salowell_bpy_lib.bevel_face_strength_mode_items( propDic[ 'bevel_settings' ][ 'face_strength_mode' ] ).name, 
            miter_outer = salowell_bpy_lib.bevel_miter_outer_items( propDic[ 'bevel_settings' ][ 'miter_outer' ] ).name, 
            miter_inner = salowell_bpy_lib.bevel_miter_inner_items( propDic[ 'bevel_settings' ][ 'miter_inner' ] ).name, 
            spread = propDic[ 'bevel_settings' ][ 'spread' ], 
            vmesh_method = salowell_bpy_lib.bevel_vmesh_method_items( propDic[ 'bevel_settings' ][ 'vmesh_method' ] ).name, 
            release_confirm = False,
            edge_selection_type = edge_selection_type
        )
        
        if len(bevel_result[0]) > 0:
            selected_face_objects.append(bevel_result[1])
            selected_face_indexes.append(bevel_result[2])
            generated_meshes.append(bevel_result[0][-1])
            selected_edge_objects.append(bevel_result[3])
            selected_edge_indexes.append(bevel_result[4])
            selected_vertex_objects.append(bevel_result[5])
            selected_vertices.append(bevel_result[6])
            
            new_blender_mesh:bmesh.types.BMesh = bevel_result[0][-1].copy()
            
            layer_map = salowell_bpy_lib.generate_bevel_layer_map(new_blender_mesh, previous_blender_mesh, bevel_result[2].copy(), edges_to_bevel.copy(), propDic[ 'bevel_settings' ][ 'segments' ])
            simple_morph_219_obj.set_layer(realCornerPropKeys[ propKey ], layer_map )
            
            layer_maps.append(layer_map)
        
        previous_blender_mesh = new_blender_mesh.copy()
    
    return generated_meshes, selected_face_objects, selected_face_indexes, selected_edge_objects, selected_edge_indexes, selected_vertex_objects, selected_vertices, layer_maps

@bpy.app.handlers.persistent
def real_corner_219_handle_edge_select_mode_click( scene, depsgraph ):
    global real_corner_219_handle_edge_select_mode_click_locked, realCorner219PropName, pie_menu_selection_data
    
    if not real_corner_219_handle_edge_select_mode_click_locked and type( scene ) is bpy.types.Scene and scene.realCorner219Layers != realCorner219PropName + '0':
        real_corner_219_handle_edge_select_mode_click_locked = True
        
        if realCorner219CurrentState == realCorner219States.SELECTING_EDGE and len(bpy.context.selected_objects) > 0 and bpy.context.object is not None and bpy.context.object.mode == 'EDIT':
            edges_to_deselect:Array = []
            
            for edge in bpy.context.selected_objects[0].data.edges:
                if edge.select:
                    edges_to_deselect.append(edge.index)
            
            bpy.context.active_object.update_from_editmode()
            
            blender_mesh:bmesh = bmesh.new()
            blender_mesh.from_mesh( bpy.context.active_object.data )
            blender_mesh.edges.ensure_lookup_table()
            
            for edge_index in edges_to_deselect:
                blender_mesh.edges[edge_index].select = False
            
            bpy.ops.object.mode_set( mode = 'OBJECT')
            blender_mesh.to_mesh(bpy.context.active_object.data)
            blender_mesh.free()
            bpy.ops.object.mode_set( mode = 'EDIT')
            
            selection_type:tuple = bpy.context.tool_settings.mesh_select_mode[:]
            
            if selection_type[0]:
                for vertex in bpy.context.active_object.data.vertices:
                    if vertex.select:
                        pie_menu_selection_data[0] = 1
                        pie_menu_selection_data[1] = vertex.index
                        bpy.ops.wm.call_menu_pie(name = 'edge_select_pie_menu')
                        break
            if selection_type[1]:
                for edge in bpy.context.active_object.data.edges:
                    if edge.select:
                        pie_menu_selection_data[0] = 2
                        pie_menu_selection_data[1] = edge.index
                        bpy.ops.wm.call_menu_pie(name = 'edge_select_pie_menu')
                        break
            if selection_type[2]:   
                for face in bpy.context.active_object.data.polygons:
                    if face.select:
                        pie_menu_selection_data[0] = 3
                        pie_menu_selection_data[1] = face.index
                        bpy.ops.wm.call_menu_pie(name = 'edge_select_pie_menu')
                        break
            
            bpy.context.active_object.update_from_editmode()
        
        real_corner_219_handle_edge_select_mode_click_locked = False

@bpy.app.handlers.persistent
def realcorner219HandleSelectDeselect( scene ) -> None:
    global realCorner219CurrentState, realCorner219SelectedBaseObjName, realCorner219ModifiedObjName, realcorner219HandleSelectDeselectFunctionLocked
    
    if realcorner219HandleSelectDeselectFunctionLocked:
        return None
    
    realcorner219HandleSelectDeselectFunctionLocked = True
    
    setRealCorner219ModeToNone:bool = False
    selectedObjs = bpy.context.selected_objects
    numOfSelObjs = len( selectedObjs )
    
    if realCorner219CurrentState == realCorner219States.SELECTING_EDGE or realCorner219CurrentState == realCorner219States.UPDATING_LAYER:
        if numOfSelObjs == 0 or numOfSelObjs > 1:
            setRealCorner219ModeToNone = True
        elif numOfSelObjs == 1:
            if selectedObjs[0].name != realCorner219ModifiedObjName:
                setRealCorner219ModeToNone = True

        if setRealCorner219ModeToNone:
            objectToReselect = []
            
            for obj in bpy.context.selected_objects:
                if obj.name != realCorner219ModifiedObjName:
                    objectToReselect.append( obj.name )
            
            currentMode = bpy.context.object.mode
            if numOfSelObjs > 0:
                bpy.ops.object.mode_set( mode = 'OBJECT')
                bpy.ops.object.select_all( action = 'DESELECT' )
            
            for obj in scene.objects:
                if obj.name == realCorner219ModifiedObjName:
                    bpy.ops.object.mode_set( mode = 'OBJECT')
                    bpy.data.objects[ realCorner219ModifiedObjName ].select_set( True )
                    bpy.ops.object.delete()
                    break
            
            if len( objectToReselect ) > 0:
                for obj in scene.objects:
                    if obj.name in objectToReselect:
                        obj.select_set( True )
            
            realCorner219CurrentState = realCorner219States.NONE
            
            bpy.data.objects[ realCorner219SelectedBaseObjName ].hide_viewport = False
            bpy.data.objects[ realCorner219SelectedBaseObjName ].select_set( True )
    elif realCorner219CurrentState == realCorner219States.UPDATING_LAYER:
        if numOfSelObjs == 0 or numOfSelObjs > 1:
            setRealCorner219ModeToNone = True
        elif numOfSelObjs == 1:
            if selectedObjs[0].name != realCorner219ModifiedObjName:
                setRealCorner219ModeToNone = True

        if setRealCorner219ModeToNone:
            realCorner219CurrentState = realCorner219States.NONE
            bpy.data.objects[ realCorner219SelectedBaseObjName ].hide_viewport = False
            salowell_bpy_lib.isolate_object_select( bpy.data.objects[ realCorner219SelectedBaseObjName ] )
    
    realcorner219HandleSelectDeselectFunctionLocked = False

    return None

@bpy.app.handlers.persistent
def realcorner219HandleSelectDeselect_2( scene ) -> None:
    if len( bpy.context.selected_objects ) == 0:
        return None
    elif not type( scene ) is bpy.types.Scene:
        return None
    
    obj = bpy.context.selected_objects[0]
    
    if not simplemorph219.simpleMorph219BaseName in obj:
        return None
    
    if not scene.realCorner219Layers in obj:
        scene.realCorner219Layers = realCorner219PropName + '0'
    
    return None

def register() -> None:
    register_class( SIMPLE_MORPH_219_REAL_CORNER_PT_panel )
    register_class( SIMPLE_MORPH_219_REAL_CORNER_OPERATIONS )
    register_class( SIMPLE_MORPH_219_REAL_CORNER_QuickOps )
    register_class( edge_select_pie_menu )
    register_class( OT_real_corner_219_handle_dynamic_edge_select )
    
    bpy.app.handlers.depsgraph_update_post.append( realcorner219HandleSelectDeselect )
    bpy.app.handlers.depsgraph_update_post.append( realcorner219HandleSelectDeselect_2 )
    bpy.app.handlers.depsgraph_update_post.append( real_corner_219_handle_edge_select_mode_click )
    bpy.app.handlers.undo_post.append( applyRealCornerUpdate )
    
    bpy.app.handlers.load_post.append( realcorner219HandleSelectDeselect )
    bpy.app.handlers.load_post.append( realcorner219HandleSelectDeselect_2 )
    bpy.app.handlers.load_post.append( real_corner_219_handle_edge_select_mode_click )
    bpy.app.handlers.load_post.append( applyRealCornerUpdate )

def unregister() -> None:
    unregister_class( SIMPLE_MORPH_219_REAL_CORNER_PT_panel )
    unregister_class( SIMPLE_MORPH_219_REAL_CORNER_OPERATIONS )
    unregister_class( SIMPLE_MORPH_219_REAL_CORNER_QuickOps )
    unregister_class( edge_select_pie_menu )
    unregister_class( OT_real_corner_219_handle_dynamic_edge_select )
    
    for h in bpy.app.handlers.depsgraph_update_post:
        if h.__name__ == 'realcorner219HandleSelectDeselect' or h.__name__ == 'realcorner219HandleSelectDeselect_2' or h.__name__ == 'real_corner_219_handle_edge_select_mode_click':
            bpy.app.handlers.depsgraph_update_post.remove( h )
    
    for h in bpy.app.handlers.undo_post:
        if h.__name__ == 'applyRealCornerUpdate':
            bpy.app.handlers.undo_post.remove( h )
    
    for h in bpy.app.handlers.load_post:
        if h.__name__ == 'realcorner219HandleSelectDeselect' or h.__name__ == 'realcorner219HandleSelectDeselect_2' or h.__name__ == 'applyRealCornerUpdate':
            bpy.app.handlers.load_post.remove( h )
