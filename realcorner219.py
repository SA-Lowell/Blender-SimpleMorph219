from ctypes import Array

from enum import Enum

import bpy

from bpy.types import Operator, Panel
from bpy.props import ( BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty )
from bpy.utils import register_class, unregister_class

import bmesh
import mathutils

from . import salowell_bpy_lib, simplemorph219

realCorner219PropName = 'realCorner219_'

class simple_morph_219_layer_map():
    """
    A comprehensive map of a single layer in a Simple Morph 219 object
    """
    blender_mesh:bmesh = None#The bmesh for this layer
    
    beveled_faces_to_original_edge:dict = {}#The newely beveled faces mapped to the original layer edge.
    beveled_faces_to_last_edge:dict = {}#The newely beveled faces mapped to the previous layer edge.
    
    beveled_vertices_to_original_edge:dict = {}#The newely beveled vertices mapped back to the original layer edge
    beveled_vertices_to_last_edge:dict = {}#The newely beveled vertices mapped back to the last edge.
    
    beveled_edges_to_original_edge:dict = {}
    beveled_edges_to_last_edge:dict = {}
    
    beveled_terminating_edges_to_last_edge:dict = {}#Edges at the end of a bevel, beyond wich there are no connecting bevels.
    beveled_terminating_edges_to_original_edge:dict = {}#Edges at the end of a bevel, beyond wich there are no connecting bevels.
    
    beveled_median_edges_to_last_edge:dict = {}#Edges formed between two beveled corners.
    beveled_median_edges_to_original_edge:dict = {}#Edges formed between two beveled corners.
    
    beveled_endstart_edges_to_original_edge:dict = {} #The edges that define the start and end of a bevel
    beveled_endstart_edges_to_last_edge:dict = {} #The edges that define the start and end of a bevel
    
    beveled_median_edges_to_last_extend_edge:dict = {}#Edges formed between two beveled edges linked to the previous edge they extend.
    
    beveled_terminating_vertices_to_last_edge:dict = {}
    beveled_terminating_vertices_to_original_edge:dict = {}
    
    beveled_median_vertices_to_last_edge:dict = {}
    beveled_median_vertices_to_original_edge:dict = {}

    def set_bmesh( self, obj:bpy.types.Object ):
        bpy.ops.object.mode_set( mode = 'OBJECT' )
        
        self.blender_mesh = bmesh.new()
        self.blender_mesh.from_mesh( obj.data )
        
    def set_empty( self ) -> None:
        self.blender_mesh = None
        
        self.beveled_faces_to_original_edge = {}
        self.beveled_faces_to_last_edge = {}
        
        self.beveled_vertices_to_original_edge = {}
        self.beveled_vertices_to_last_edge = {}
        
        self.beveled_edges_to_original_edge = {}
        self.beveled_edges_to_last_edge = {}
        
        self.beveled_terminating_edges_to_last_edge = {}
        self.beveled_terminating_edges_to_original_edge = {}
        
        self.beveled_median_edges_to_last_edge = {}
        self.beveled_median_edges_to_original_edge = {}
        
        self.beveled_endstart_edges_to_original_edge = {}
        self.beveled_endstart_edges_to_last_edge = {}
        
        self.beveled_median_edges_to_last_extend_edge = {}
        
        self.beveled_terminating_vertices_to_last_edge = {}
        self.beveled_terminating_vertices_to_original_edge = {}
        
        self.beveled_median_vertices_to_last_edge = {}
        self.beveled_median_vertices_to_original_edge = {}

class simple_morph_219_object():
    """
    Stores a comprehensive history of any object generated through SimpleMorph219
    """
    obj:object = None
    object_name:str = ''
    base_data_set:bool = False
    base_object_name:str = ''
    base_object:object = None
    base_vertices:int = 0
    base_edges:int = 0
    base_faces:int = 0
    
    vertex_history_map:Array = []
    edge_history_map:Array = []
    face_history_map:Array = []
    
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
            
            return True

        return False
    
    def get_layer_map_from_name( self, layer_name:str ) -> simple_morph_219_layer_map:
        if layer_name == ''    :
            return None
        
        if layer_name in self.layer_maps:
            return self.layer_maps[ layer_name ] 
        
        self.layer_maps[ layer_name ] = simple_morph_219_layer_map()
        
        return self.layer_maps[ layer_name ]

    def map_beveled_mesh_to_previous_layer( self, original_mesh:bmesh, new_mesh:bmesh, new_faces:Array, new_layer_map:simple_morph_219_layer_map ) -> dict | dict | dict:
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
        processed_original_faces:Array = []
        processed_new_faces:Array = []
        queued_original_faces:Array = []
        queued_new_faces:Array = []
        
        processed_original_edges:Array = []
        processed_new_edges:Array = []
        
        vertex_map:dict = {}
        edge_map:dict = {}
        face_map:dict = {}
        
        for last_edge_index in new_layer_map.beveled_endstart_edges_to_last_edge:
            original_bmesh_faces_from_edge_tmp:Array = salowell_bpy_lib.get_faces_of_edge_bmesh( original_mesh, last_edge_index )[1]
            original_bmesh_faces_from_edge:Array = []
            
            for original_bmesh_face_from_edge_id in original_bmesh_faces_from_edge_tmp:
                if not original_bmesh_face_from_edge_id in processed_original_faces:
                    original_bmesh_faces_from_edge.append( original_bmesh_face_from_edge_id )
                    processed_original_faces.append( original_bmesh_face_from_edge_id )
            
            if len( original_bmesh_faces_from_edge ) == 0:
                continue
            
            new_edge_indexes = new_layer_map.beveled_endstart_edges_to_last_edge[ last_edge_index ]
            
            for new_edge_index in new_edge_indexes:
                new_bmesh_faces_from_edge_tmp:Array = salowell_bpy_lib.get_faces_of_edge_bmesh( new_mesh, new_edge_index )[1]
                new_bmesh_faces_from_edge:Array = []
                
                for _, new_bmesh_face_from_edge_id in enumerate( new_bmesh_faces_from_edge_tmp ):
                    if not new_bmesh_face_from_edge_id in new_faces and not new_bmesh_face_from_edge_id in processed_new_faces:
                        new_bmesh_faces_from_edge.append( new_bmesh_face_from_edge_id )
                        processed_new_faces.append( new_bmesh_face_from_edge_id )
                
                if len( new_bmesh_faces_from_edge ) == 0:
                    continue
                
                paired = salowell_bpy_lib.pair_closest_faces( new_mesh, new_bmesh_faces_from_edge, original_mesh, original_bmesh_faces_from_edge )
                
                for pair in paired:
                    face_map[pair[1]] = pair[0]
                    
                    new_edges:Array = salowell_bpy_lib.get_edges_of_face_bmesh( new_mesh, pair[0] )[1]
                    original_edges:Array = salowell_bpy_lib.get_edges_of_face_bmesh( original_mesh, pair[1] )[1]
                    
                    vertices_on_new_endstart_edge:Array = []
                    
                    for new_edges_from_last_ids in new_layer_map.beveled_endstart_edges_to_last_edge:
                        for new_edges_from_last_id in new_layer_map.beveled_endstart_edges_to_last_edge[ new_edges_from_last_ids ]:
                            if not new_mesh.edges[ new_edges_from_last_id ].verts[0].index in vertices_on_new_endstart_edge:
                                vertices_on_new_endstart_edge.append( new_mesh.edges[ new_edges_from_last_id ].verts[0].index )
                            
                            if not new_mesh.edges[ new_edges_from_last_id ].verts[1].index in vertices_on_new_endstart_edge:
                                vertices_on_new_endstart_edge.append( new_mesh.edges[ new_edges_from_last_id ].verts[1].index )
                    
                    for index, _ in enumerate(new_edges):
                        if not new_edges[ index ] in processed_new_edges and not original_edges[ index ] in new_layer_map.beveled_endstart_edges_to_last_edge:
                            edge_map[ original_edges[ index ] ] = new_edges[ index ]
                            
                            connected_previous_edge_id:int = original_edges[ index - 1 ]
                            connected_next_edge_id:int = new_edges[ index - 1 ]
                            
                            paired_vertices:dict = salowell_bpy_lib.pair_edge_vertices( original_mesh, original_edges[ index ], connected_previous_edge_id, new_mesh, new_edges[ index ], connected_next_edge_id )
                            
                            for _, paired_previous_id in enumerate( paired_vertices ):
                                if not paired_previous_id in vertex_map and not paired_vertices[ paired_previous_id ] in vertices_on_new_endstart_edge:
                                    vertex_map[ paired_previous_id ] = paired_vertices[ paired_previous_id ]
                            
                            processed_original_edges.append( original_edges[ index ] )
                            processed_new_edges.append( new_edges[ index ] )
                        
                        new_faces_of_edge = salowell_bpy_lib.get_faces_of_edge_bmesh( new_mesh, new_edges[ index ] )[1]
                        original_faces_of_edge = salowell_bpy_lib.get_faces_of_edge_bmesh( original_mesh, original_edges[ index ] )[1]
                        
                        for face_of_edge_index, face_of_edge in enumerate( new_faces_of_edge ):
                            if not original_faces_of_edge[ face_of_edge_index ] in processed_original_faces and not original_faces_of_edge[ face_of_edge_index ] in queued_original_faces:
                                queued_original_faces.append( original_faces_of_edge[ face_of_edge_index ] )
                            
                            if not face_of_edge in new_faces and not face_of_edge in processed_new_faces and not face_of_edge in queued_new_faces:
                                queued_new_faces.append( face_of_edge )
                
                while len( queued_new_faces ) > 0:
                    queue_new:int = queued_new_faces.pop()
                    queue_original:int = queued_original_faces.pop()
                    processed_original_faces.append( queue_original )
                    processed_new_faces.append( queue_new )
                    
                    face_map[ queue_original ] = queue_new
                    
                    new_edges = salowell_bpy_lib.get_edges_of_face_bmesh( new_mesh, queue_new )[1]
                    original_edges = salowell_bpy_lib.get_edges_of_face_bmesh( original_mesh, queue_original )[1]
                    
                    vertices_on_new_endstart_edge:Array = []
                    
                    for new_edges_from_last_ids in new_layer_map.beveled_endstart_edges_to_last_edge:
                        for new_edges_from_last_id in new_layer_map.beveled_endstart_edges_to_last_edge[ new_edges_from_last_ids ]:
                            if not new_mesh.edges[ new_edges_from_last_id ].verts[0].index in vertices_on_new_endstart_edge:
                                vertices_on_new_endstart_edge.append( new_mesh.edges[ new_edges_from_last_id ].verts[0].index )
                            
                            if not new_mesh.edges[ new_edges_from_last_id ].verts[1].index in vertices_on_new_endstart_edge:
                                vertices_on_new_endstart_edge.append( new_mesh.edges[ new_edges_from_last_id ].verts[1].index )
                    
                    for index, new_edge_id in enumerate( new_edges ):
                        if not new_edge_id in processed_new_edges and not original_edges[ index ] in new_layer_map.beveled_endstart_edges_to_last_edge:
                            edge_map[ original_edges[ index ] ] = new_edge_id
                            
                            connected_previous_edge_id:int = original_edges[ index - 1 ]
                            connected_next_edge_id:int = new_edges[ index - 1 ]
                            
                            paired_vertices:dict = salowell_bpy_lib.pair_edge_vertices( original_mesh, original_edges[ index ], connected_previous_edge_id, new_mesh, new_edge_id, connected_next_edge_id )
                            
                            for paired_index, paired_previous_id in enumerate( paired_vertices ):
                                if not paired_previous_id in vertex_map and not paired_vertices[ paired_previous_id ] in vertices_on_new_endstart_edge:
                                    vertex_map[ paired_previous_id ] = paired_vertices[ paired_previous_id ]
                            
                            processed_original_edges.append( original_edges[ index ] )
                            processed_new_edges.append( new_edge_id )
                        
                        new_faces_of_edge = salowell_bpy_lib.get_faces_of_edge_bmesh( new_mesh, new_edges[ index ] )[1]
                        original_faces_of_edge = salowell_bpy_lib.get_faces_of_edge_bmesh( original_mesh, original_edges[ index ] )[1]
                        
                        for face_of_edge_index, face_of_edge in enumerate( new_faces_of_edge ):
                            if not face_of_edge in new_faces and not face_of_edge in processed_new_faces and not face_of_edge in queued_new_faces and not original_faces_of_edge[ face_of_edge_index ] in processed_original_faces and not original_faces_of_edge[ face_of_edge_index ] in queued_original_faces:
                                queued_new_faces.append( face_of_edge )
                                queued_original_faces.append( original_faces_of_edge[ face_of_edge_index ] )
        
        return vertex_map, edge_map, face_map

    def gen_selected_bevels_map(self, layer_index_key ) -> None:
        real_corner_prop_keys = get_all_real_corner_custom_prop_keys( self.obj )
        layer_index = get_real_corner_custom_prop_key_index( self.obj, layer_index_key )
        duplicate_object:object = None
        
        for index in range( 0, layer_index + 1) :
            if duplicate_object is not None:
                bpy.ops.object.delete()
            
            bpy.ops.object.mode_set( mode = 'OBJECT')
            
            salowell_bpy_lib.isolate_object_select( bpy.data.objects[ self.object_name ] )
            
            duplicate_object = bpy.context.selected_objects[0]
            
            selected_faces = gen_real_corner_mesh( duplicate_object, real_corner_prop_keys[ index ] )[1]
            previous_Layer_selected_edges = realCornerPropIndexToDict( bpy.data.objects[ self.object_name ], real_corner_prop_keys[ index ] )[ 'edges' ]
            previous_Layer_selected_edges_order = salowell_bpy_lib.array_map_low_to_high_numbers( previous_Layer_selected_edges )[0]
            selected_vertices = salowell_bpy_lib.get_selected_vertices( duplicate_object )[1]
            selected_edges = salowell_bpy_lib.get_selected_edges( duplicate_object )[1]
            bevel_faces_grouped_grouped:Array = []
            _, bounding_edges_grouped_indexes, _, bounding_edges_indexes = salowell_bpy_lib.get_bounding_edges_of_selected_face_groups( bpy.context.selected_objects[0] )
            
            edge_indexes_processed:Array = []
            processed_faces:Array = []
            bevel_faces_grouped:Array = [[]] * len( previous_Layer_selected_edges )
            
            for face_group in bounding_edges_grouped_indexes:
                for edge_group in face_group:
                    edge_group_order = salowell_bpy_lib.array_map_low_to_high_numbers( edge_group )[0]
                    
                    for edge_group_index, edge_index in enumerate( edge_group ):
                        #Do not reprocess an edge that has already been processed
                        if edge_index not in edge_indexes_processed:
                            edge_indexes_processed.append( edge_index )
                            edge_group_order[ edge_group_index ]#This will return the high low order of the current edge_group_index
                            
                            selected_faces_of_edge:Array = salowell_bpy_lib.get_faces_of_edge( bpy.data.objects[ self.object_name ], edge_index, 1 )[1]
                            bevel_faces:Array = []#All faces of a bevel segment
                            edges_of_face:Array = []
                            
                            if len( selected_faces_of_edge ) == 1:
                                edges_of_face = salowell_bpy_lib.get_edges_of_face(bpy.data.objects[ self.object_name ], selected_faces_of_edge[0], 1 )[1]
                            
                            primary_edge:int = edge_index
                            
                            #Looping through each of the faces in this bevel. Starting with 1 and will shrink + grow as more are found + queried.
                            while len( selected_faces_of_edge ) > 0:
                                selected_face_index = selected_faces_of_edge.pop()
                                if selected_face_index not in bevel_faces and selected_face_index not in processed_faces:
                                    processed_faces.append(selected_face_index)
                                    face_is_bevel:bool = True
                                    edges_of_face = salowell_bpy_lib.get_edges_of_face(bpy.data.objects[ self.object_name ], selected_face_index, 1 )[1]
                                    
                                    #Looping through all edges[edges_of_face] of this face[selected_face_index]
                                    
                                    edge_is_bounding_edge_count:int = 0
                                    
                                    #Looping through each of the edges in the current face 
                                    for edge_of_face in edges_of_face:
                                        if edge_of_face in edge_group and edge_of_face != primary_edge and len( bevel_faces ) > 0:
                                            face_is_bevel = False
                                            break
                                        
                                        #If this edge[edge_of_face] is a bounding edge of a bevel and is also not the [primary_edge] we are testing we need to make note of this and then move on to the next edge.
                                        if edge_of_face in bounding_edges_indexes and edge_of_face != primary_edge:
                                            edge_is_bounding_edge_count += 1
                                            break
                                        
                                        #If this edge[edge_of_face] has already been processed and it's not the [primary_edge] we are testing lets move on to the next [edge_of_face].
                                        if edge_of_face in edge_indexes_processed and edge_of_face != primary_edge:
                                            continue
                                        
                                        if not edge_of_face in edge_indexes_processed:
                                            edge_indexes_processed.append(edge_of_face)
                                        
                                        edge_1:bpy.types.MeshEdge = bpy.data.objects[ self.object_name ].data.edges[ edge_of_face ]
                                        edge_2:bpy.types.MeshEdge = bpy.data.objects[ self.object_name ].data.edges[ primary_edge ]
                                        
                                        #If the edge we are checking is not connected to the original edge we were testing [neither of its vertices match the original] this means edge_of_face/edge_1 is on the opposite side in the case of a 4 sided polygon (beveled edges should always be comprised of 4 sided faces excluding certain edges/sudden stops and corners.)
                                        if edge_1.vertices[0] != edge_2.vertices[0] and edge_1.vertices[1] != edge_2.vertices[0] and edge_1.vertices[0] != edge_2.vertices[1] and edge_1.vertices[1] != edge_2.vertices[1]:
                                            primary_edge = edge_1.index
                                            faces_of_primary_edge = salowell_bpy_lib.get_faces_of_edge( bpy.data.objects[ self.object_name ], primary_edge, 1 )[1]
                                            
                                            for face_of_primary_edge in faces_of_primary_edge:
                                                if not face_of_primary_edge in processed_faces:
                                                    selected_faces_of_edge.append( face_of_primary_edge )
                                    
                                    if edge_is_bounding_edge_count == len( edges_of_face ):
                                        face_is_bevel = False
                                    
                                    if face_is_bevel:
                                        bevel_faces.append(selected_face_index)
                        
                        if len( bevel_faces ) != 0:
                            bevel_faces_grouped[previous_Layer_selected_edges_order.index(edge_group_order[edge_group_index])] = bevel_faces
                
                bevel_faces_grouped_grouped.append([i for i in bevel_faces_grouped if i != []])
        
        return bevel_faces_grouped_grouped

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

def update_real_corner_bevel_values( op, context ):
    global update_real_corner_bevel_values_locked, realCorner219CurrentState, realCorner219States, realCorner219LastUpdate
    
    if update_real_corner_bevel_values_locked:
        return None
    
    objectNameToQueryPropertiesFrom:str = op.originalObjectName
    if realCorner219CurrentState == realCorner219States.UPDATING_LAYER and op.placeholderObjectName != '':
        objectNameToQueryPropertiesFrom = op.placeholderObjectName
    
    realCornerPropDict = realCornerPropStringToDict( bpy.data.objects[ objectNameToQueryPropertiesFrom ][ op.real_corner_layer_name ] )
    
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
        realCornerPropDictToString( realCornerPropDict )
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
            items.append( ( realCornerKey, 'Layer ' + realCornerKeyLayerStr, 'Editing Real Corner layer ' + realCornerKeyLayerStr ) )
            realCornerKeyLayer += 1
    
    return items

def createRealCornerCustomPropKeyIfNoneExists( obj ):
    keyArray = get_all_real_corner_custom_prop_keys( obj )
    
    if len( keyArray ) == 0:
        keyArray.append( createNewRealCornerCustomProperty( obj, realCorner219PropName ) )
    
    return keyArray

def get_real_corner_custom_prop_key_index( obj, propKey):
    index:int = 0
    found:bool = False
    
    for key, value in obj.items():
        if type( value ) is str and value.startswith( '0(' ):
            if key == propKey:
                found = True
                break
            index += 1
    
    if not found:
        index = -1
    
    return index

def get_all_real_corner_custom_prop_keys( obj ):
    realCornerKeys = []
    
    for key, value in obj.items():
        if type( value ) is str and value.startswith( '0(' ) and key.startswith( realCorner219PropName ) :
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

def createNewRealCornerCustomProperty( obj, keyName ):
    normalizeRealCornerCustomPropertyNames( obj )
    suffix = 0
    keyNameWithSuffix = keyName + str( suffix )
    
    for key, _ in obj.items():
        if key == keyNameWithSuffix:
            suffix += 1
        elif key.startswith( keyName ):
            break
        
        keyNameWithSuffix = keyName + str( suffix )
    
    obj[ keyNameWithSuffix ] = realCornerPropDictToString( createEmptyRealCornerPropDict() )
    
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
                    
                    edges_of_vertex = salowell_bpy_lib.get_edge_indexes_from_vertex_index( bpy.context.selected_objects[0].data, vertex, -1 )
                    
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
            ( "TURN_ON_EDGE_SELECT", "Turn On Real Corner 219 Edge Select", "Turns on the Real Corner 219 Edge Select mode."),
            ( "TURN_OFF_AND_SAVE_EDGE_SELECT", "Turn Off Real Corner 219 Edge Select and save", "Turns off the Real Corner 219 Edge Select mode and saves the currently selected edges."),
        ]
    )
    
    def execute( self, context ):
        global realCorner219CurrentState, realCorner219SelectedBaseObjName, realCorner219ModifiedObjName, realcorner219HandleSelectDeselectFunctionLocked
        
        if self.action == 'TEST_QUICK':
            test_obj = simple_morph_219_object(context.selected_objects[0].name)
            print(test_obj.gen_selected_bevels_map('realCorner219_0'))
            #supporting_edge_loop_length:float = 0.1
            #createSupportingEdgeLoopsAroundSelectedFaces( bpy.context.selected_objects[0], supporting_edge_loop_length )
            
            return { 'FINISHED' }
        if self.action == 'APPLY_REAL_CORNER_CHANGES':
            pass
        elif self.action == 'TURN_ON_EDGE_SELECT':
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
            
            genRealCornerMeshAtPrevIndex( bpy.data.objects[ realCorner219ModifiedObjName ], context.scene.realCorner219Layers )
            realCorner219ModifiedObjName = context.selected_objects[0].name
            realcorner219HandleSelectDeselectFunctionLocked = False
            bpy.data.objects[ realCorner219SelectedBaseObjName ].hide_viewport = True
        elif self.action == 'TURN_OFF_AND_SAVE_EDGE_SELECT':
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
                realCornerPropDict[ 'edges' ] = selectedEdgesToCustomPropArray( modifiedObject )
                originalObject[ context.scene.realCorner219Layers ] = realCornerPropDictToString( realCornerPropDict )
            
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
            ( "ADD_LAYER", "Add Layer", "Adds a new bevel layer to the mesh" ),
            ( "MARK_AS_219_BASE", "Mark As 219 Base", "Marks the current object as a base object for all Simple Morph operations." ),
            ( "UPDATE_LAYER", "Update Layer", "Initiates the operator menu for setting the bevel layer's settings" )
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
        layout = self.layout
        layout.label( text = 'Updating Layer ' + str( self.real_corner_layer_index ) )
        
        affect_column = layout.column()
        affect_input = affect_column.prop( self, property = "affect", text = 'Affect', expand = True)
        affect_column.enabled = False
        
        offset_type_column = layout.column()
        offset_type_input = offset_type_column.prop( self, property = "offset_type", text = 'Width Type' )
        
        offset_column = layout.column()
        offset_input = offset_column.prop( self, property = "offset", text = 'Width' )
        
        offset_pct_column = layout.column()
        offset_pct_input = offset_pct_column.prop( self, property = "offset_pct", text = 'Width Percent' )

        segments_column = layout.column()
        segments_input = segments_column.prop( self, property = "segments", text = "Segments" )
        
        profile_column = layout.column()
        profile_input = profile_column.prop( self, property = "profile", text = "Shape" )
        
        material_column = layout.column()
        material_input = material_column.prop( self, property = "material", text = "Material Index" )
        
        harden_normals_column = layout.column()
        harden_normals_input = harden_normals_column.prop( self, property = "harden_normals", text = "Harden Normals" )
        
        clamp_overlap_column = layout.column()
        clamp_overlap_input = clamp_overlap_column.prop( self, property = "clamp_overlap", text = "Clamp Overlap" )
        
        loop_slide_column = layout.column()
        loop_slide_input = loop_slide_column.prop( self, property = "loop_slide", text = "Loop Slide" )
        
        mark_seam_column = layout.column()
        mark_seam_input = mark_seam_column.prop( self, property = "mark_seam", text = "Seams" )
        
        mark_sharp_column = layout.column()
        mark_sharp_input = mark_sharp_column.prop( self, property = "mark_sharp", text = "Sharp" )
        
        miter_outer_column = layout.column()
        miter_outer_input = miter_outer_column.prop( self, property = "miter_outer", text = "Outer" )
        
        miter_inner_column = layout.column()
        miter_inner_input = miter_inner_column.prop( self, property = "miter_inner", text = "Inner" )
        
        spread_column = layout.column()
        spread_input = spread_column.prop( self, property = "spread", text = "Spread" )
        
        vmesh_method_column = layout.column()
        vmesh_method_input = vmesh_method_column.prop( self, property = "vmesh_method", text = "Intersection Type" )
        
        face_strength_mode_column = layout.column()
        face_strength_mode_input = face_strength_mode_column.prop( self, property = "face_strength_mode", text = "Face Strength" )
        
        profile_type_column = layout.column()
        profile_type_input = profile_type_column.prop( self, property = "profile_type", text = "Profile Type", expand = True )
        profile_type_column.enabled = False

    def execute( self, context ):
        global realCorner219CurrentState, realCorner219SelectedBaseObjName, realCorner219ModifiedObjName, realcorner219HandleSelectDeselectFunctionLocked, update_real_corner_bevel_values_locked
        
        selectedObject = bpy.context.selected_objects
        
        if len( selectedObject ) == 0:
            return { 'CANCELLED' }
        
        selectedObject = selectedObject[0]
        
        if self.action == 'ADD_LAYER':
            createNewRealCornerCustomProperty( bpy.data.objects[ self.originalObjectName ], realCorner219PropName )
            return { 'CANCELLED' }
        elif self.action == 'MARK_AS_219_BASE':
            simplemorph219.markObjectAsSimpleMorphBaseObject( bpy.data.objects[ self.originalObjectName ] )
            return { 'CANCELLED' }
        elif self.action == 'UPDATE_LAYER':
            realcorner219HandleSelectDeselectFunctionLocked = True
            realCorner219CurrentState = realCorner219States.UPDATING_LAYER
            realCorner219SelectedBaseObjName = selectedObject.name
            salowell_bpy_lib.isolate_object_select( selectedObject )

            realCornerPropDict = realCornerPropStringToDict( bpy.data.objects[ self.originalObjectName ][ self.real_corner_layer_name ] )
            
            self.affect = salowell_bpy_lib.bevel_affect_items( realCornerPropDict[ 'bevel_settings' ][ 'affect' ] ).name
            self.offset_type = salowell_bpy_lib.bevel_offset_type_items( realCornerPropDict[ 'bevel_settings' ][ 'offset_type' ] ).name
            self.offset = realCornerPropDict[ 'bevel_settings' ][ 'offset' ]
            self.offset_pct = realCornerPropDict[ 'bevel_settings' ][ 'offset_pct' ]
            self.segments = realCornerPropDict[ 'bevel_settings' ][ 'segments' ]
            self.profile = realCornerPropDict[ 'bevel_settings' ][ 'profile' ]
            self.material = realCornerPropDict[ 'bevel_settings' ][ 'material' ]
            self.harden_normals = realCornerPropDict[ 'bevel_settings' ][ 'harden_normals' ]
            self.clamp_overlap = realCornerPropDict[ 'bevel_settings' ][ 'clamp_overlap' ]
            self.loop_slide = realCornerPropDict[ 'bevel_settings' ][ 'loop_slide' ]
            self.mark_seam = realCornerPropDict[ 'bevel_settings' ][ 'mark_seam' ]
            self.mark_sharp = realCornerPropDict[ 'bevel_settings' ][ 'mark_sharp' ]
            self.miter_outer = salowell_bpy_lib.bevel_miter_outer_items( realCornerPropDict[ 'bevel_settings' ][ 'miter_outer' ] ).name
            self.miter_inner = salowell_bpy_lib.bevel_miter_inner_items( realCornerPropDict[ 'bevel_settings' ][ 'miter_inner' ] ).name
            self.spread = realCornerPropDict[ 'bevel_settings' ][ 'spread' ]
            self.vmesh_method = salowell_bpy_lib.bevel_vmesh_method_items( realCornerPropDict[ 'bevel_settings' ][ 'vmesh_method' ] ).name
            self.face_strength_mode = salowell_bpy_lib.bevel_face_strength_mode_items( realCornerPropDict[ 'bevel_settings' ][ 'face_strength_mode' ] ).name
            self.profile_type = salowell_bpy_lib.bevel_profile_type_items( realCornerPropDict[ 'bevel_settings' ][ 'profile_type' ] ).name
            
            bpy.data.objects[ self.originalObjectName ][ self.real_corner_layer_name ] = realCornerPropDictToString( realCornerPropDict )
            
            bpy.ops.object.mode_set( mode = 'OBJECT')
            bpy.ops.object.duplicate()
            bpy.data.objects[ self.originalObjectName ].hide_viewport = True
            updatedObject = context.selected_objects[0]
            updatedObject[ simplemorph219.simpleMorph219BaseName ] = False
            salowell_bpy_lib.isolate_object_select( updatedObject )
            realCorner219ModifiedObjName = updatedObject.name
            gen_real_corner_mesh( updatedObject, self.real_corner_layer_name )
            self.placeholderObjectName = context.selected_objects[0].name
            realcorner219HandleSelectDeselectFunctionLocked = False
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
            
            gen_real_corner_mesh( updatedObject, self.real_corner_layer_name )
            self.placeholderObjectName = context.selected_objects[0].name
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
            createLayerObj = createLayerBtn.operator( 'simplemorph.219_real_corner_operations_op', text = 'Add Layer' )
            createLayerObj.action = 'ADD_LAYER'
            createLayerObj.originalObjectName = selectedObject.name
        
        if simplemorph219.isSimpleMorphBaseObject( selectedObject ) and selectedObject is not None and realCorner219CurrentState == realCorner219States.NONE:
            turnOnEditModeBtn = layout.column()
            turnOnEditModeObj = turnOnEditModeBtn.operator( 'realcorner219.real_corner_quickops_op', text = 'Turn On Edge Select Mode' )
            turnOnEditModeObj.action = 'TURN_ON_EDGE_SELECT'
        elif ( simplemorph219.isSimpleMorphBaseObject( selectedObject ) or simplemorph219.isSimpleMorphTempBaseObject( selectedObject ) ) and selectedObject is not None and realCorner219CurrentState == realCorner219States.SELECTING_EDGE:
            turnOffEditModeBtn = layout.column()
            turnOffEditModeObj = turnOffEditModeBtn.operator( 'realcorner219.real_corner_quickops_op', text = 'Save and Turn Off Edge Select Mode' )
            turnOffEditModeObj.action = 'TURN_OFF_AND_SAVE_EDGE_SELECT'
        
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
            updateLayerObj = updateLayerBtn.operator( 'simplemorph.219_real_corner_operations_op', text = 'Update Layer' )
            
            if not simplemorph219.isSimpleMorphBaseObject( selectedObject ):
                updateLayerBtn.enabled = False
            
            updateLayerObj.action = 'UPDATE_LAYER'
            updateLayerObj.real_corner_layer_name = realCorner219LayerIndex
            updateLayerObj.real_corner_layer_index = get_real_corner_custom_prop_key_index( context.selected_objects[0], realCorner219LayerIndex )
            updateLayerObj.originalObjectName = selectedObject.name
            updateLayerObj.objectLayerBeingModified = context.scene.realCorner219Layers

    def execute( self, context ):
        bevelLayers = get_all_real_corner_custom_prop_keys( context.selected_objects[0] )

        if len( bevelLayers ) == 0:
            keyName = createNewRealCornerCustomProperty( context.selected_objects[0], realCorner219PropName )
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
    me = obj.data
    bm:bmesh = bmesh.new()
    bm.from_mesh( me )
    
    return salowell_bpy_lib.get_selected_edges( obj )[1]

def createEmptyRealCornerPropDict() -> dict:
    realCornerPropDict:dict = {}
    realCornerPropDict[ 'edges' ] = []
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

def realCornerPropDictToString( realCornerPropDict:dict ) -> str:
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
    
    realCornerPropString:str = '0(' + ','.join( str( edgeId ) for edgeId in realCornerPropDict[ 'edges' ] ) + ')'
    realCornerPropString = realCornerPropString + '(' + affect + ',' + offset_type + ',' + offset + ',' + offset_pct + ',' + segments + ',' + profile + ',' + material + ',' + harden_normals + ',' + clamp_overlap + ',' + loop_slide + ',' + mark_seam + ',' + mark_sharp + ',' + miter_outer + ',' + miter_inner + ',' + spread + ',' + vmesh_method + ',' + face_strength_mode + ',' + profile_type + ')'
    
    return realCornerPropString

def realCornerPropIndexToDict( obj:object, propKey:str ) -> dict:
    return realCornerPropStringToDict( obj[ propKey ] )

def realCornerPropStringToDict( realCornerPropString:str ) -> str:
    realCornerPropDict = createEmptyRealCornerPropDict()
    #realCornerPropDict:dict = {}
    #realCornerPropDict[ 'edges' ] = []
    #realCornerPropDict[ 'bevel_settings' ] = {}
    #realCornerPropDict[ 'bevel_settings' ][ 'segments' ]:int = 1
    #realCornerPropDict[ 'bevel_settings' ][ 'offset' ]:float = 0.001
    
    propertyValues = realCornerPropString.strip().lstrip( '0' ).lstrip( '(' ).rstrip( ')' ).split( ')(' )
    
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
    
    return realCornerPropDict

#This is currently a hacky solution for updating. I need to learn the correct design paradigm for Blender's API.
@bpy.app.handlers.persistent
def applyRealCornerUpdate( scene ) -> None:
    global realCorner219LastUpdate
    
    if len( realCorner219LastUpdate ) != 0:
        bpy.data.objects[ realCorner219LastUpdate[0] ][ realCorner219LastUpdate[1] ] = realCorner219LastUpdate[2]
        realCorner219LastUpdate = []

def genRealCornerMeshAtPrevIndex( obj, layerIndexKey ) -> None:
    propKeyIndex = get_real_corner_custom_prop_key_index( obj, layerIndexKey )
    
    if propKeyIndex > 0:
        propKeyIndex -= 1
        PropKeysArr = get_all_real_corner_custom_prop_keys( obj )
        gen_real_corner_mesh( obj, PropKeysArr[ propKeyIndex ] )

def gen_real_corner_mesh( obj, layerIndexKey ) -> None:
    realCornerPropKeys = get_all_real_corner_custom_prop_keys( obj )
    layerIndex = get_real_corner_custom_prop_key_index( obj, layerIndexKey )
    
    bpy.ops.object.mode_set( mode = 'EDIT')
    
    for propKey in range( 0, layerIndex + 1 ):
        bpy.ops.mesh.select_mode( type = 'EDGE' )
        bpy.ops.mesh.select_all( action = 'DESELECT' )
        
        propDic = realCornerPropIndexToDict( obj, realCornerPropKeys[ propKey ] )
        bpy.ops.object.mode_set( mode = 'OBJECT' )
        
        for i in bpy.context.selected_objects[0].data.polygons:
            i.select = False
        
        for i in bpy.context.selected_objects[0].data.edges:
            i.select = False
        
        for i in bpy.context.selected_objects[0].data.vertices:
            i.select = False
        
        for edgeIndex in propDic[ 'edges' ]:
            bpy.context.selected_objects[0].data.edges[ edgeIndex ].select = True
        
        return salowell_bpy_lib.bevel(
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
            release_confirm = False
        )

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
            bpy.ops.object.mode_set( mode = 'OBJECT')
            bpy.ops.object.select_all( action = 'DESELECT' )
            
            for obj in scene.objects:
                if obj.name == realCorner219ModifiedObjName:
                    bpy.data.objects[ realCorner219ModifiedObjName ].select_set( True )
                    bpy.ops.object.delete()
                    break
            
            if len( objectToReselect ) > 0:
                for obj in scene.objects:
                    if obj.name in objectToReselect:
                        obj.select_set( True )
            
            realCorner219CurrentState = realCorner219States.NONE
            bpy.data.objects[ realCorner219SelectedBaseObjName ].hide_viewport = False
            
            bpy.ops.object.mode_set( mode = currentMode )
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
    
    bpy.app.handlers.depsgraph_update_post.append( realcorner219HandleSelectDeselect )
    bpy.app.handlers.depsgraph_update_post.append( realcorner219HandleSelectDeselect_2 )
    bpy.app.handlers.undo_post.append( applyRealCornerUpdate )
    
    bpy.app.handlers.load_post.append( realcorner219HandleSelectDeselect )
    bpy.app.handlers.load_post.append( realcorner219HandleSelectDeselect_2 )
    bpy.app.handlers.load_post.append( applyRealCornerUpdate )

def unregister() -> None:
    unregister_class( SIMPLE_MORPH_219_REAL_CORNER_PT_panel )
    unregister_class( SIMPLE_MORPH_219_REAL_CORNER_OPERATIONS )
    unregister_class( SIMPLE_MORPH_219_REAL_CORNER_QuickOps )
    
    for h in bpy.app.handlers.depsgraph_update_post:
        if h.__name__ == 'realcorner219HandleSelectDeselect' or h.__name__ == 'realcorner219HandleSelectDeselect_2':
            bpy.app.handlers.depsgraph_update_post.remove( h )
    
    for h in bpy.app.handlers.undo_post:
        if h.__name__ == 'applyRealCornerUpdate':
            bpy.app.handlers.undo_post.remove( h )
    
    for h in bpy.app.handlers.load_post:
        if h.__name__ == 'realcorner219HandleSelectDeselect' or h.__name__ == 'realcorner219HandleSelectDeselect_2' or h.__name__ == 'applyRealCornerUpdate':
            bpy.app.handlers.load_post.remove( h )
