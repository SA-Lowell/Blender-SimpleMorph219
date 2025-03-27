import logging
from ctypes import Array
from enum import Enum

import random

from . import realcorner219

import bpy
import bmesh
import mathutils

error_logger_219 = logging.getLogger(__name__)

class bevel_affect_items( Enum ):
    VERTICES = 0
    EDGES = 1

class bevel_offset_type_items( Enum ):
    OFFSET = 0
    WIDTH = 1
    DEPTH = 2
    PERCENT = 3
    ABSOLUTE = 4

class bevel_miter_outer_items( Enum ):
    SHARP = 0
    PATCH = 1
    ARC = 2

class bevel_miter_inner_items( Enum ):
    SHARP = 0
    ARC = 1

class bevel_vmesh_method_items( Enum ):
    ADJ = 0
    CUTOFF = 1

class bevel_face_strength_mode_items( Enum ):
    NONE = 0
    NEW = 1
    AFFECTED = 2
    ALL = 3

class bevel_profile_type_items( Enum ):
    SUPERELLIPSE = 0
    CUSTOM = 1

def get_selected_layer_index() -> int:
    return realcorner219.get_real_corner_custom_prop_key_index(bpy.context.selected_objects[0], bpy.context.scene.realCorner219Layers)

def unwrapObjectUV( objectToUnwrap ):
    isolate_object_select( objectToUnwrap )
    bpy.ops.object.mode_set( mode = 'EDIT' )
    bpy.ops.mesh.select_mode( type = 'VERT' )
    bpy.ops.mesh.select_all( action = 'DESELECT' )
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    
    for vertex in objectToUnwrap.data.vertices:
        vertex.select = True
    
    bpy.ops.object.mode_set(mode = 'EDIT')
    
    lm =  objectToUnwrap.data.uv_layers.get( 'UVMap' )
    if not lm:
        lm = objectToUnwrap.data.uv_layers.new( name = 'UVMap' )
    
    lm.active = True
    
    bpy.ops.object.mode_set( mode = 'EDIT' )
    bpy.ops.uv.unwrap( method = 'CONFORMAL', fill_holes = False, correct_aspect = False, use_subsurf_data = False, margin_method = 'SCALED', margin = 0.0)
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    
    #This is hooking into the Texel Density addon to automatically set the TD based on your current TD settings https://mrven.gumroad.com/l/CEIOR
    #If you don't have the plugin installed it will skip over the texel density calculation.
    if hasattr(bpy.ops.object, 'texel_density_set'):
        bpy.ops.object.texel_density_set()
    
    #TODO: Grab the UV islands and handle them each separately.
    #uvIslands:list = bpy_extras.mesh_utils.mesh_linked_uv_islands(bpy.context.active_object.data)
    
    uvCenter = [0.0, 0.0]
    uvCount = 0
    
    for loop in objectToUnwrap.data.loops:
        uvCenter[0] += objectToUnwrap.data.uv_layers.active.data[ loop.index ].uv[0]
        uvCenter[1] += objectToUnwrap.data.uv_layers.active.data[ loop.index ].uv[1]
        uvCount += 1
    
    uvCenter[0] = uvCenter[0] / uvCount
    uvCenter[1] = uvCenter[1] / uvCount
    
    uvNewCenter = [ random.uniform( 0.0, 1.0 ), random.uniform( 0.0, 1.0 ) ]
    
    uvNewCenter[0] = uvNewCenter[0] - uvCenter[0]
    uvNewCenter[1] = uvNewCenter[1] - uvCenter[1]
    
    for loop in objectToUnwrap.data.loops:
        objectToUnwrap.data.uv_layers.active.data[loop.index].uv = (objectToUnwrap.data.uv_layers.active.data[loop.index].uv[0] + uvNewCenter[0], objectToUnwrap.data.uv_layers.active.data[loop.index].uv[1] + uvNewCenter[1])

#Unselects all objects except the passed in Object. Selects the passed in object if it's not already selected.
#Also returns the objects that were selected before this change is made along with the select mode.
def isolate_object_select( objectToIsolate ):
    selectedObjects = bpy.context.selected_objects
    selectedMode = None
    
    if bpy.context.object is not None:
        selectedMode = bpy.context.object.mode
    
    bpy.context.view_layer.objects.active = objectToIsolate
    
    if bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set( mode = 'OBJECT' )
    
    selected_object_names:Array = []
    
    for selected_object in bpy.context.selected_objects:
        selected_object_names.append(selected_object.name)
    
    for select_object_name in selected_object_names:
        if select_object_name != objectToIsolate.name:
            bpy.context.scene.objects[ select_object_name ].select_set( False )
    
    objectToIsolate.select_set( True )
    
    return selectedObjects, selectedMode

class SimpleMorph219BlenderState:
    selected_objects:Array = []
    mode:str = ''
    
    def __init__( self ) -> None:
        self.set_this_to_current_blender_state()
    
    def set_this_to_current_blender_state( self ) -> None:
        self.mode = bpy.context.object.mode
        self.selected_objects = []
        
        bpy.ops.object.mode_set( mode = 'OBJECT' )
        
        for obj in bpy.context.selected_objects:
            self.selected_objects.append(obj.name)
        
        self.set_blender_state_to_this()
    
    def set_blender_state_to_this( self ) -> None:
        bpy.ops.object.mode_set( mode = 'OBJECT' )
        bpy.ops.object.select_all( action = 'DESELECT' )
        
        for obj_name in self.selected_objects:
            bpy.context.scene.objects[ obj_name ].select_set( True )
        
        bpy.ops.object.mode_set( mode = self.mode )

def pair_closest_faces( blender_mesh_1:bmesh, mesh_1_face_indexes:Array, blender_mesh_2:bmesh, mesh_2_face_indexes:Array ):
    """
    Pairs up the closest faces from two lists of arrays in two meshes.
    
    Parameters
    ----------
    blender_mesh_1: bmesh
        The first bmesh
    
    mesh_1_face_indexes: Array
        An array of face indexes within blender_mesh_1
    
    blender_mesh_2: bmesh
        The second bmesh
    
    mesh_2_face_indexes: Array
        An array of face indexes within blender_mesh_2
    
    Returns
    -------
        An array of faces paired up in closest order.
        [
            [
                face ID from mesh 1,
                face ID from mesh 2
            ],
            [
                face ID from mesh 1,
                face ID from mesh 2
            ]
        ]
    """
    mesh_1_face_centers:Array = []
    mesh_2_face_centers:Array = []
    paired_closest:Array = []
    
    for _, mesh_1_face_id in enumerate( mesh_1_face_indexes ):
        mesh_1_face_centers.append( blender_mesh_1.faces[ mesh_1_face_id ].calc_center_median() )
    
    for _, mesh_2_face_id in enumerate( mesh_2_face_indexes ):
        mesh_2_face_centers.append( blender_mesh_2.faces[ mesh_2_face_id ].calc_center_median() )
    
    for mesh_1_face_center_index, mesh_1_face_center in enumerate( mesh_1_face_centers ):
        last_distance:int = -1
        current_distance:int = -1
        shortest_distance:float = 0.0
        mesh_2_face_shortest_distance_index:int = -1
        
        for mesh_2_face_center_index, mesh_2_face_center in enumerate( mesh_2_face_centers ):
            current_distance = ( mesh_1_face_center - mesh_2_face_center ).length
            
            if last_distance == -1:
                mesh_2_face_shortest_distance_index = mesh_2_face_center_index
                shortest_distance = current_distance
            else:
                if current_distance < shortest_distance:
                    shortest_distance = current_distance
                    mesh_2_face_shortest_distance_index = mesh_2_face_center_index
            
            last_distance = current_distance
        
        paired_closest.append( [ mesh_1_face_indexes[ mesh_1_face_center_index ], mesh_2_face_indexes[ mesh_2_face_shortest_distance_index ] ] )
        
        del mesh_2_face_centers[ mesh_2_face_shortest_distance_index ]
        del mesh_2_face_indexes[ mesh_2_face_shortest_distance_index ]
    
    return paired_closest

def arrays_equal(array1:Array, array2:Array) -> bool:
    if len(array1) != len(array2):
        return False
    
    for index, value in enumerate(array1):
        if array1[index] != array2[index]:
            return False
    
    return True
#select_state might seem weird but it's important to use when a calling function very specifically needs faces that only exist in a certain select state.
#TODO: The if statements that select_state uses are weird, but I never got around to changing them before fully testing everything.
def get_faces_of_edge_bmesh( blender_mesh:bmesh, edge:int, select_state:int = 0, selected_faces:Array = [] ) -> Array | Array:
    """
    Retrieves the indexes of every single face the input edge is connected to.

    Parameters
    ----------
    obj: bmesh
        The bmesh that edge belongs to. This is the bmesh that will be parsed for all connected faces.

    edge: int
        Index of the edge you want to find all connected faces of.
    
    select_state : int, default 0
        Types of edges to return
            0 = all,
            1 = selected only,
            -1 = unselected only
    
    Returns
    -------
        An array of indexes for each face that is connected to the input edge.
    """
    owner_faces:Array = []
    owner_faces_indexes:Array = []
    
    mesh = blender_mesh
    found_first:bool = False

    if hasattr( mesh.verts, "ensure_lookup_table" ): 
        mesh.verts.ensure_lookup_table()
    if hasattr( mesh.edges, "ensure_lookup_table" ): 
        mesh.edges.ensure_lookup_table()
    if hasattr( mesh.faces, "ensure_lookup_table" ): 
        mesh.faces.ensure_lookup_table()
    
    if select_state == 1:
        for face in mesh.edges[edge].link_faces:
            if not face.index in owner_faces_indexes and face.index in selected_faces:
                owner_faces.append( face )
                owner_faces_indexes.append( face.index )
    elif select_state == -1:
        for face in mesh.edges[edge].link_faces:
            if not face.index in owner_faces_indexes and not face.index in selected_faces:
                owner_faces.append( face )
                owner_faces_indexes.append( face.index )
    else:
        for face in mesh.edges[edge].link_faces:
            if not face.index in owner_faces_indexes:
                owner_faces.append( face )
                owner_faces_indexes.append( face.index )
    
    return owner_faces, owner_faces_indexes

def get_faces_of_edge( obj:bpy.types.Object, edge:int, select_state:int = 0 ) -> Array | Array:
    """
    Retrieves the indexes of every single face the input edge is connected to.

    Parameters
    ----------
    obj: bpy.types.Object
        The object that edge belongs to. This is the object that will be parsed for all connected faces.

    edge: int
        Index of the edge you want to find all connected faces of.
    
    select_state : int, default 0
        Types of edges to return
            0 = all,
            1 = selected only,
            -1 = unselected only
    
    Returns
    -------
        An array of indexes for each face that is connected to the input edge.
    """
    owner_faces:Array = []
    owner_faces_indexes:Array = []
    
    mesh = obj.data
    found_first:bool = False
    
    if select_state == 1:
        for face in mesh.polygons:
            found_first = False
            
            if not face in owner_faces and face.select:
                for _, value in enumerate( face.vertices ):#TODO: THIS FOR LOOP IS SLOW AND THE MAIN PROBLEM!
                    if value == mesh.edges[ edge ].vertices[0] or value == mesh.edges[ edge ].vertices[1]:
                        if found_first:
                            owner_faces.append( face )
                            owner_faces_indexes.append( face.index )
                            break
                        
                        found_first = True
    elif select_state == -1:
        for face in mesh.polygons:
            found_first = False
            
            if not face in owner_faces and not face.select:
                for _, value in enumerate( face.vertices ):#TODO: THIS FOR LOOP IS SLOW AND THE MAIN PROBLEM!
                    if value == mesh.edges[ edge ].vertices[0] or value == mesh.edges[ edge ].vertices[1]:
                        if found_first:
                            owner_faces.append( face )
                            owner_faces_indexes.append( face.index )
                            break
                        
                        found_first = True
    else:
        for face in mesh.polygons:
            found_first = False
            
            if not face in owner_faces:
                for _, value in enumerate( face.vertices ):#TODO: THIS FOR LOOP IS SLOW AND THE MAIN PROBLEM!
                    if value == mesh.edges[ edge ].vertices[0] or value == mesh.edges[ edge ].vertices[1]:
                        if found_first:
                            owner_faces.append( face )
                            owner_faces_indexes.append( face.index )
                            break
                        
                        found_first = True
    
    return owner_faces, owner_faces_indexes

def get_edge_index_from_polygon_list(mesh:bpy.types.Mesh, polygonList:Array, vertex1:int, vertex2:int) -> int:
    """
    Given a mesh, list of polygons in that mesh (Used to optimize search time speed in the case you have a small pool of faces to query)
    and the indexes of an edge's vertices, this will return the indnex of that edge inside of the Mesh.
    """
    edge_index:int = -1
    
    if mesh is not None:
        for polygonIndex in polygonList:
            for edge in mesh.polygons[ polygonIndex ].edge_keys:
                if ( edge[0] == vertex1 and edge[1] == vertex2 ) or ( edge[0] == vertex2 and edge[1] == vertex1 ):
                    edge_index = edge.index
                    break
    
    return edge_index

def get_edge_index_from_vertex_indexes(mesh:bpy.types.Mesh, vertex1:int, vertex2:int) -> int:
    edge_index:int = -1
    
    if mesh is not None:
        for edge in mesh.edges:
            if ( edge.vertices[0] == vertex1 and edge.vertices[1] == vertex2 ) or ( edge.vertices[0] == vertex2 and edge.vertices[1] == vertex1 ):
                edge_index = edge.index
                break
    
    return edge_index

def array_map_low_to_high_numbers(array:Array = []) -> Array:
    """
    Returns two arrays that show the proper order of the values inside of the input array.
    
    Parameters
    ----------
    array: Array
        An array of numbers you wish to have their orders mapped
    
    Returns
    -------
        original_order_mapped
            An array that maps the low to high order of each value.
            ie: [48, 55, 35, 22] = [2, 3, 1, 0]
        reordered_mapped
            An array that maps the low to high reordered values back to the original array.
            ie: [48, 55, 35, 22] = [22, 35, 48, 55] = [3, 2, 0, 1]
    """
    original_order_mapped:Array = []
    reordered_mapped:Array = []
    array_copy:Array = []
    
    for arr_value in array:
        if not isinstance(arr_value, int) and not isinstance(arr_value, float):
            return []
    
    array_copy = array.copy()
    array_copy.sort()
    
    for array_copy_val in array_copy:
        reordered_mapped.append( array.index( array_copy_val ) )
        
    for array_val in array:
        original_order_mapped.append( array_copy.index( array_val ) )
    
    return original_order_mapped, reordered_mapped

def get_edges_of_vertex( mesh:bmesh.types.BMesh, vertex:int, select_state:int = 0, selected_edges:Array = [] ) -> Array:
    """
    Retrieves the indexes of every single edge connected to the input vertex index.

    Parameters
    ----------
    mesh: bmesh.types.BMesh, Object.data converted to a bmesh
        The Mesh you want to retrieve vertices from

    vertex: int
        The ID/Index of the vertex
    
    select_state: int, default 0
        Types of edges to return
            0 = all,
            1 = selected only,
            -1 = unselected only
    
    Returns
    -------
        An array of indexes for each edge that is connected to the input vertex.
    """
    select_state = -1 if select_state < -1 else select_state
    select_state = 1 if select_state > 1 else select_state
    
    edge_indexes:Array = []
    
    if mesh is not None:
        if select_state == 0:
            edge_indexes = [ edge.index for edge in mesh.edges if edge.verts[0].index == vertex or edge.verts[1].index == vertex ]
        elif select_state == 1:
            edge_indexes = [ edge.index for edge in mesh.edges if ( edge.verts[0].index == vertex or edge.verts[1].index == vertex ) and edge.index in selected_edges ]
        else:
            edge_indexes = [ edge.index for edge in mesh.edges if ( edge.verts[0].index == vertex or edge.verts[1].index == vertex ) and edge.index not in selected_edges ]
    
    return edge_indexes

def map_edge_keys_to_edges(mesh:bmesh.types.BMesh , selected_only:bool = False) -> dict:
    """
    Used to map a mesh's edge_keys to its MeshEdge objects

    Parameters
    ----------
    mesh : bpy.types.Mesh, Object.data
        The Mesh you want to map the edge_keys for

    selected_only : bool, default False
        Whether this should map all edges or only the currently selected edges.
    
    Returns
    -------
        [
            MeshPolygon.edge_keys[0] => MeshEdge,
            ...,
            MeshPolygon.edge_keys[n] => MeshEdge,
        ]
    """
    mapped_edges:dict = {}
    
    for edge in mesh.edges:
        mapped_edges[(edge.verts[0].index, edge.verts[1].index)] = edge
    
    return mapped_edges

def separate_orphaned_and_faced_edges( blender_mesh:bmesh.types.BMesh, edges:Array ) -> Array | Array | dict:
    """
    Takes the selected edges [edges] and separates out edges that form faces and those that do not (those that are orphaned)
    
    Parameters
    ----------
        obj : bpy.types.Object
            The object with a bpy.types.Mesh that contains edges found in the edges parameter.
        
        edges: Array
            Contains the IDs of all edges you wish to process from obj.data
    
    Returns
    -------
        First array contains a list of all orphaned edges
        Second array contains a list of all edges that form faces
        Third paramater, a dict, contains a list of all edges that form faces grouped by the faces they form (This dict will, naturally, contain duplicate edges in certain cases, ie: If two or more faces are touching. This dict will be indexed by face IDs)
    """
    grouped_edges_by_face:dict = {}
    face_edges:Array = [] #List of all edges that form full faces
    orphaned_edges:Array = []
    
    obj_edge_count:int = len( blender_mesh.edges )
    
    blender_mesh.edges.ensure_lookup_table()
    
    for edge_index in edges:
        if edge_index < obj_edge_count:
            blender_mesh.edges[ edge_index ].select = True
    
    full_faces = get_selected_faces( blender_mesh )[1]
    
    for face_index in full_faces:
        edges_of_face = get_edges_of_face_bmesh( blender_mesh, face_index)[1]
        grouped_edges_by_face[ face_index ] = edges_of_face
        
        for face_edge_index in edges_of_face:
            if not face_edge_index in face_edges:
                face_edges.append( face_edge_index )
    
    for edge_index in edges:
        if not edge_index in face_edges:
            orphaned_edges.append(edge_index)
    
    return orphaned_edges, face_edges, grouped_edges_by_face, 

def order_edges_by_pathing(blender_mesh:bmesh.types.BMesh, edge_ids:Array) -> Array:
    """
    Returns an array of the edge ids sorted in a pathing-like order.
    The function starts with the smallest id. It then paths out to every other branched edge. Splits use the lower ID value as precedence.
    If the edges have multiple islands, it will iterate over them independently, ordered by the islands with the smallest values first, and then the smallest value of each island first in that island.
    
    Parameters
    ----------
        blender_mesh : bmesh.types.BMesh
            The Blender Mesh that contains the given edge_ids
        
        edge_ids: Array
            A list of the edge IDs you wish to order.
    
    Returns
    -------
        An array of the edge_ids reordered in a pathing-like format
    """
    blender_mesh.verts.ensure_lookup_table()
    blender_mesh.edges.ensure_lookup_table()
    edge_ids_ordered = edge_ids.copy()
    edge_ids_ordered.sort()
    processed_edge_ids:Array = []
    queued_grouped_edge_ids:Array = []
    sorted_order:Array = []

    for edge_id in edge_ids_ordered:
        if edge_id not in queued_grouped_edge_ids and edge_id not in processed_edge_ids:
            queued_grouped_edge_ids.append(edge_id)
        
            while(len(queued_grouped_edge_ids) > 0):
                processing_edge_id:int = queued_grouped_edge_ids[0]
                del queued_grouped_edge_ids[0]
                
                processing_edge_vertex_id_1:int = blender_mesh.edges[processing_edge_id].verts[0].index
                processing_edge_vertex_id_2:int = blender_mesh.edges[processing_edge_id].verts[1].index
                
                if processing_edge_id not in processed_edge_ids:
                    processed_edge_ids.append(processing_edge_id)
                    sorted_order.append(processing_edge_id)
                    next_edges:Array = []
                    
                    for ordered_edge_id in edge_ids_ordered:
                        if ordered_edge_id not in processed_edge_ids:
                            ordered_edge_vertex_id_1:int = blender_mesh.edges[ordered_edge_id].verts[0].index
                            ordered_edge_vertex_id_2:int = blender_mesh.edges[ordered_edge_id].verts[1].index
                            
                            if processing_edge_vertex_id_1 == ordered_edge_vertex_id_1 or processing_edge_vertex_id_2 == ordered_edge_vertex_id_2 or processing_edge_vertex_id_1 == ordered_edge_vertex_id_2 or processing_edge_vertex_id_2 == ordered_edge_vertex_id_1:
                                next_edges.append(ordered_edge_id)
                                pass
                    
                    next_edges.sort()
                    
                    if len(next_edges) > 0:
                        queued_grouped_edge_ids = next_edges + queued_grouped_edge_ids
    
    return sorted_order

#TODO: If you order the pre-bevel edges by ID number (0-n), and then order the newly created bevel faces by id number (0-n), you can pair them up using these ordered values!!!!!.
#Do not try to dsetermine left and right based on largest and smallest faces in each row. The order can swap here.
def generate_bevel_layer_map(new_blender_mesh:bmesh.types.BMesh, previous_blender_mesh:bmesh.types.BMesh, new_bevel_face_ids_in:Array, previous_unbeveled_edge_ids_in:Array, bevel_segments:int) -> dict:
    bounding_edge_ids = get_bounding_edges_of_face_groups(new_blender_mesh, new_bevel_face_ids_in)[3]
    layer_map:realcorner219.simple_morph_219_layer_map = realcorner219.simple_morph_219_layer_map()
    layer_map.set_empty()
    layer_map.blender_mesh = new_blender_mesh.copy()
    layer_map.previous_selected_edges = previous_unbeveled_edge_ids_in.copy()
    layer_map.previous_blender_mesh = previous_blender_mesh.copy()

    new_bevel_face_ids_ordered:Array = new_bevel_face_ids_in.copy()
    new_bevel_face_ids_ordered.sort()

    #This variable is a copy of the new faces but without the terminator faces. The terminator faces are *always* the lower bounds of new face IDs, while the actual columns that were formed from the previous edge are always the upper bounds of the IDs.
    non_terminator_start_index:int = len(new_bevel_face_ids_in) - (bevel_segments * len(previous_unbeveled_edge_ids_in))
    new_bevel_face_ids_ordered_without_terminators:Array = new_bevel_face_ids_ordered[non_terminator_start_index:]
    
    new_bevel_terminator_and_corner_faces_grouped:Array = get_grouped_faces(new_blender_mesh, new_bevel_face_ids_ordered[0:non_terminator_start_index])
    processed_new_bevel_terminator_and_corner_faces_grouped:Array = []
    
    previous_unbeveled_edge_ids_ordered:Array = previous_unbeveled_edge_ids_in.copy()
    previous_unbeveled_edge_ids_ordered.sort()
    
    previous_unbeveled_edge_ids_pathed = order_edges_by_pathing(previous_blender_mesh, previous_unbeveled_edge_ids_in)
    
    for previous_unbeveled_edge_id in previous_unbeveled_edge_ids_pathed:
        layer_map.beveled_faces_to_last_edge[previous_unbeveled_edge_id] = []
        layer_map.beveled_parallel_edges_to_last_edge[previous_unbeveled_edge_id] = []
        layer_map.beveled_endstart_edges_to_last_edge[previous_unbeveled_edge_id] = []
        layer_map.beveled_median_edges_to_last_edge[previous_unbeveled_edge_id] = [[],[]]
    
    start_edge_id:int = 0
    end_edge_id:int = 0
    left_edge_id:int = 0
    right_edge_id:int = 0
    
    processed_faces:Array = []
    processed_previous_vertices:Array = []
    
    seed:bool = True
    
    previous_unbeveled_edge_normals:dict = {}
    
    for previous_unbeveled_edge_id in previous_unbeveled_edge_ids_pathed:
        vert_0:mathutils.Vector = mathutils.Vector( (previous_blender_mesh.edges[previous_unbeveled_edge_id].verts[0].co[0], previous_blender_mesh.edges[previous_unbeveled_edge_id].verts[0].co[1],previous_blender_mesh.edges[previous_unbeveled_edge_id].verts[0].co[2]) )
        vert_1:mathutils.Vector = mathutils.Vector( (previous_blender_mesh.edges[previous_unbeveled_edge_id].verts[1].co[0], previous_blender_mesh.edges[previous_unbeveled_edge_id].verts[1].co[1],previous_blender_mesh.edges[previous_unbeveled_edge_id].verts[1].co[2]) )
        
        previous_unbeveled_edge_normals[previous_unbeveled_edge_id] = vert_0 - vert_1
        previous_unbeveled_edge_normals[previous_unbeveled_edge_id].normalize()
    
    index:int = 0
    
    faces_per_column:int = bevel_segments
    
    for previous_unbeveled_edge_id  in previous_unbeveled_edge_ids_pathed:
        previous_unbeveled_edge_id_index = previous_unbeveled_edge_ids_ordered.index(previous_unbeveled_edge_id)
        
        faces_of_column_range_start:int = previous_unbeveled_edge_id_index * faces_per_column
        faces_of_column:Array = new_bevel_face_ids_ordered_without_terminators[faces_of_column_range_start:faces_of_column_range_start + faces_per_column]
        
        parallel_starting_edge:int = 0
        smallest_angle:float = 0.0
        
        first_bounding_edge:bool = True
        
        face_edge_index:int = 0
        
        for edge in new_blender_mesh.faces[faces_of_column[0]].edges:
            if edge.index in bounding_edge_ids:
                vert0:mathutils.Vector = mathutils.Vector( (edge.verts[0].co[0], edge.verts[0].co[1], edge.verts[0].co[2]) )
                vert1:mathutils.Vector = mathutils.Vector( (edge.verts[1].co[0], edge.verts[1].co[1], edge.verts[1].co[2]) )
                normal:mathutils.Vector = vert0 - vert1
                normal.normalize()
                
                #Adjusting for corners that have collapsed/overlapping edges and, thus, causing zero length vectors for some edges.
                #This fix assumes the previous edge of the face isn't also zero. It take the cross product of the current face's normal and previous edge on that face to create a perpendicular normal vector that should be fairly close to what the current edge *SHOULD* be if it hadn't collapsed during the bevel.
                if normal.length == 0:
                    previous_edge:bmesh.types.BMEdge = new_blender_mesh.faces[faces_of_column[0]].edges[face_edge_index - 1]
                    face_normal:mathutils.Vector = new_blender_mesh.faces[faces_of_column[0]].normal
                    vert0 = mathutils.Vector( (previous_edge.verts[0].co[0], previous_edge.verts[0].co[1], previous_edge.verts[0].co[2]) )
                    vert1 = mathutils.Vector( (previous_edge.verts[1].co[0], previous_edge.verts[1].co[1], previous_edge.verts[1].co[2]) )
                    normal = face_normal.cross(vert0 - vert1)
                    normal.normalize()
                
                new_angle:float = normal.angle(previous_unbeveled_edge_normals[previous_unbeveled_edge_id])
                
                if first_bounding_edge:
                    smallest_angle = new_angle
                    parallel_starting_edge = edge.index
                    first_bounding_edge = False
                else:
                    if new_angle < smallest_angle:
                        smallest_angle = new_angle
                        parallel_starting_edge = edge.index
            
            face_edge_index += 1
        
        start_edge_id, end_edge_id, left_edge_id, right_edge_id = get_left_right_start_end_edges_from_start_edge_id( new_blender_mesh, faces_of_column[0], parallel_starting_edge )[0:4]
        
        left_faces:Array = get_faces_of_edge_bmesh( new_blender_mesh, left_edge_id, 1, new_bevel_face_ids_ordered )[1]
        right_faces:Array = get_faces_of_edge_bmesh( new_blender_mesh, right_edge_id, 1, new_bevel_face_ids_ordered )[1]
        
        seed:bool = True
        end_start_face_of_bounding_column:int = 0
        
        for left_face in left_faces:
            if left_face != faces_of_column[0] and left_face in processed_faces:
                end_start_face_of_bounding_column = left_face
                seed = False
                
        for right_face in right_faces:
            if right_face != faces_of_column[0] and right_face in processed_faces:
                end_start_face_of_bounding_column = right_face
                seed = False
        
        reverse_order:bool = False
        
        if not seed:
            for previous_edge in layer_map.beveled_faces_to_last_edge:
                if end_start_face_of_bounding_column in layer_map.beveled_faces_to_last_edge[previous_edge]:
                    if layer_map.beveled_faces_to_last_edge[previous_edge].index(end_start_face_of_bounding_column) != 0:
                        reverse_order = True
                        break
        
        parallel_edges:Array = []
        left_edges:Array = []
        right_edges:Array = []
        
        first_face_in_column:bool = True
        
        for face_of_column in faces_of_column:
            anchor_edge:int = 0
            if first_face_in_column:
                anchor_edge = start_edge_id
                first_face_in_column = False
            else:
                anchor_edge = end_edge_id
            
            start_edge_id, end_edge_id, left_edge_id, right_edge_id = get_left_right_start_end_edges_from_start_edge_id( new_blender_mesh, face_of_column, anchor_edge )[0:4]
            
            if start_edge_id not in parallel_edges:
                parallel_edges.append(start_edge_id)
            
            if end_edge_id not in parallel_edges:
                parallel_edges.append(end_edge_id)
            
            if left_edge_id not in left_edges:
                left_edges.append(left_edge_id)
            if right_edge_id not in right_edges:
                right_edges.append(right_edge_id)
        
        if reverse_order:
            parallel_edges.reverse()
            left_edges.reverse()
            right_edges.reverse()
            faces_of_column.reverse()
            
            left_edges_tmp:Array = right_edges
            right_edges = left_edges
            left_edges = left_edges_tmp
        
        layer_map.beveled_faces_to_last_edge[previous_unbeveled_edge_id] = faces_of_column
        layer_map.beveled_parallel_edges_to_last_edge[previous_unbeveled_edge_id] = parallel_edges
        layer_map.beveled_endstart_edges_to_last_edge[previous_unbeveled_edge_id] = [parallel_edges[0], parallel_edges[-1]]
        layer_map.beveled_median_edges_to_last_edge[previous_unbeveled_edge_id] = [left_edges, right_edges]
        
        left_vertices:Array = []
        right_vertices:Array = []
        
        left_edges_index:int = 0
        first_left_vertex_id:int = 0
        left_vertices_swap:bool = False
        
        for left_edge_id in left_edges:
            left_edge_vertex_0_id = new_blender_mesh.edges[left_edge_id].verts[0].index
            left_edge_vertex_1_id = new_blender_mesh.edges[left_edge_id].verts[1].index
            
            if left_edge_vertex_0_id not in left_vertices:
                left_vertices.append(left_edge_vertex_0_id)
            
            if left_edge_vertex_1_id not in left_vertices:
                left_vertices.append(left_edge_vertex_1_id)
            
            if left_edges_index == 0:
                first_left_vertex_id = left_edge_vertex_0_id
            else:
                if left_edge_vertex_0_id == first_left_vertex_id or left_edge_vertex_1_id == first_left_vertex_id:
                    left_vertices_swap = True
                
            left_edges_index += 1
        
        if left_vertices_swap:
            first_left_vertex_index:int = left_vertices[0]
            left_vertices[0] = left_vertices[1]
            left_vertices[1] = first_left_vertex_index
        
        right_edges_index:int = 0
        first_right_vertex_id:int = 0
        right_vertices_swap:bool = False

        for right_edge_id in right_edges:
            right_edge_vertex_0_id = new_blender_mesh.edges[right_edge_id].verts[0].index
            right_edge_vertex_1_id = new_blender_mesh.edges[right_edge_id].verts[1].index
            
            if right_edge_vertex_0_id not in right_vertices:
                right_vertices.append(right_edge_vertex_0_id)
            
            if right_edge_vertex_1_id not in right_vertices:
                right_vertices.append(right_edge_vertex_1_id)
            
            if right_edges_index == 0:
                first_right_vertex_id = right_edge_vertex_0_id
            else:
                if right_edge_vertex_0_id == first_right_vertex_id or right_edge_vertex_1_id == first_right_vertex_id:
                    right_vertices_swap = True
        
        if right_vertices_swap:
            first_right_vertex_index:int = right_vertices[0]
            right_vertices[0] = right_vertices[1]
            right_vertices[1] = first_right_vertex_index
        
        layer_map.beveled_median_vertices_to_last_edge[previous_unbeveled_edge_id] = [left_vertices, right_vertices]
        
        previous_unbeveled_vertex_small:int = previous_blender_mesh.edges[previous_unbeveled_edge_id].verts[0].index
        previous_unbeveled_vertex_large:int = previous_blender_mesh.edges[previous_unbeveled_edge_id].verts[1].index
        
        if previous_unbeveled_vertex_small > previous_unbeveled_vertex_large:
            previous_unbeveled_vert_tmp:int = previous_unbeveled_vertex_small
            previous_unbeveled_vertex_small = previous_unbeveled_vertex_large
            previous_unbeveled_vertex_large = previous_unbeveled_vert_tmp
        
        new_small_vertices:Array = left_vertices
        new_large_vertices:Array = right_vertices
        
        new_small_vertices.sort()
        new_large_vertices.sort()
        
        if new_small_vertices[0] < new_large_vertices[0]:
            new_small_vertices = left_vertices
            new_large_vertices = right_vertices
        else:
            new_small_vertices = right_vertices
            new_large_vertices = left_vertices

        previous_unbeveled_vertices:Array = [previous_unbeveled_vertex_small, previous_unbeveled_vertex_large]
        previous_unbeveled_vertex_index:int = 0
        
        for previous_unbeveled_vertex in previous_unbeveled_vertices:
            #If the vertex ID of this line[previous_unbeveled_edge_id] has not already been processed.
            if previous_unbeveled_vertex not in processed_previous_vertices:
                processed_previous_vertices.append(previous_unbeveled_vertex)
                
                vertex_face_group_index:int = 0
                
                #Looping through the GROUPED corners/terminator (as faces)
                for vertex_face_group in new_bevel_terminator_and_corner_faces_grouped:
                    #If this corner/terminator group has not already been processed/linked to a vertex on the previous mesh.
                    if vertex_face_group_index not in processed_new_bevel_terminator_and_corner_faces_grouped:
                        match_found:bool = False
                        #Now lets loop through each of the individual faces within this corner/terminator group.
                        for face_id in vertex_face_group:
                            #Looping through every single vertex inside of this face.
                            for face_vertex in new_blender_mesh.faces[face_id].verts:
                                if (previous_unbeveled_vertex_index == 0 and face_vertex.index in new_small_vertices) or (previous_unbeveled_vertex_index == 1 and face_vertex.index in new_large_vertices):
                                    match_found = True
                                    break
                            
                            if match_found:
                                break
                        
                        if match_found:
                            processed_new_bevel_terminator_and_corner_faces_grouped.append(vertex_face_group_index)
                            layer_map.beveled_faces_to_last_vertex[previous_unbeveled_vertex] = vertex_face_group
                            
                            vertex_face_group_edges:Array = get_edges_from_faces(new_blender_mesh, vertex_face_group)
                            vertex_face_group_vertices:Array = get_vertices_from_edges(new_blender_mesh, vertex_face_group_edges)
                            
                            layer_map.beveled_edges_to_last_vertex[previous_unbeveled_vertex] = vertex_face_group_edges
                            layer_map.beveled_vertices_to_last_vertex[previous_unbeveled_vertex] = vertex_face_group_vertices
                    
                    vertex_face_group_index += 1
            
            previous_unbeveled_vertex_index += 1
        
        processed_faces = processed_faces + faces_of_column
        index += 1
    
    previous_map:tuple = realcorner219.map_beveled_mesh_to_previous_layer(original_mesh = previous_blender_mesh, new_mesh = new_blender_mesh, new_faces = new_bevel_face_ids_in, new_layer_map = layer_map)
    layer_map.unbeveled_vertices = previous_map[0]
    layer_map.unbeveled_edges = previous_map[1]
    layer_map.unbeveled_faces = previous_map[2]
    
    return layer_map

def get_edges_from_faces(blender_mesh:bmesh.types.BMesh, face_ids:Array) -> Array:
    """
    Returns an array of all unique edge IDs found across all the given face_ids within blender_mesh
    
    Parameters
    ----------
        blender_mesh : bmesh.types.BMesh
            The Blender Mesh that contains the faces.
        
        face_ids: Array
            A list of all the face IDs to query within blender_mesh
    
    Returns
    -------
        An array of all the edge IDs found within the face_ids of blender_mesh. This will not contain any duplicates.
    """
    blender_mesh.edges.ensure_lookup_table()
    
    edge_ids:Array = []
    
    for face_id in face_ids:
        for edge in blender_mesh.faces[face_id].edges:
            if edge.index not in edge_ids:
                edge_ids.append(edge.index)
    
    return edge_ids

def get_vertices_from_edges(blender_mesh:bmesh.types.BMesh, edge_ids:Array) -> Array:
    """
    Returns an array of all unique vertex IDs found across all the given edge_ids within blender_mesh
    
    Parameters
    ----------
        blender_mesh : bmesh.types.BMesh
            The Blender Mesh that contains the edges.
        
        edge_ids: Array
            A list of all the edge IDs to query within blender_mesh
    
    Returns
    -------
        An array of all the vertex IDs found within the edge_ids of blender_mesh. This will not contain any duplicates.
    """
    blender_mesh.verts.ensure_lookup_table()
    
    vertex_ids:Array = []
    
    for edge_id in edge_ids:
        for vertex in blender_mesh.edges[edge_id].verts:
            if vertex.index not in vertex_ids:
                vertex_ids.append(vertex.index)
    
    return vertex_ids
    
def get_left_right_start_end_edges_from_start_edge_id( blender_mesh:bmesh.types.BMesh, quad_face_id, start_edge_id ) -> int |  int |  int |  int |  int |  int |  int |  int:
    """
    Returns the edges that represent the start, end, left, and right edges of the input quad, quad_face_id, relative to the edge ID passed in for start_edge_id.
    The first 4 return values are the actual IDs of those edges within the mesh, and the last 4 are the indexes of those edges relative to the input quad, quad_face_id.
    The distinction between ID and index here is important, as the is is the overall edge's ID within the entire object, but the index is the index within the face's .edges property.
    
    Parameters
    ----------
        blender_mesh : bmesh.types.BMesh
            The Blender Mesh that contains the face and edge.
        
        quad_face_id: int
            the ID of the face within blender_mesh. This face *MUST* be a quad otherwise None is returned for all 8 values.
        
        start_edge_id: int
            The ID of the edge within blender_mesh. This edge must also be part of the input face.
    
    Returns
    -------
        start_edge_id
            ID of the starting edge.
        
        end_edge_id
            ID of the edge opposite of the starting edge.
        
        left_edge_id
            ID of the edge next to the starting edge, counter clockwise when looking down from the side of the face normal.
        
        right_edge_id
            ID of the edge next to the starting edge, clockwise when looking down from the side of the face normal.
        
        start_edge_index
             Index of the starting edge within the input face's .edges property.
        
        end_edge_index
            Index of the edge opposite of the starting edge from within the face's .edges property.
        
        left_edge_index
            Index of the edge next to the starting edge, counter clockwise when looking down from the side of the face normal, from within the face's .edges property.
        
        right_edge_index
            Index of the edge next to the starting edge, clockwise when looking down from the side of the face normal, from within the face's .edges property.
    """
    edges_of_face:Array = get_edges_of_face_bmesh( blender_mesh, quad_face_id )[1]
    
    if len(edges_of_face) != 4:
        error_logger_219.warning('219 Error: Non quad face passed into "get_left_right_start_end_edges_from_start_edge_id()". quad_face_id: ' + str(quad_face_id) + ', start_edge_id: ' + str(start_edge_id) + ', Object Name: ' + bpy.context.active_object.name)
        return None, None, None, None, None, None, None, None

    if start_edge_id not in edges_of_face:
        error_logger_219.warning('219 Error: quad_face_id[' + str(quad_face_id) + '] passed into "get_left_right_start_end_edges_from_start_edge_id()". Does not contain start_edge_id[' + str(start_edge_id) + '] within Bmesh ' + str(blender_mesh))
        return None, None, None, None, None, None, None, None
    
    start_edge_index = edges_of_face.index( start_edge_id )
    
    end_edge_id:int = edges_of_face[ start_edge_index - 2 ]
    left_edge_id:int = edges_of_face[ start_edge_index - 3 ]
    right_edge_id:int = edges_of_face[ start_edge_index - 1 ]
    
    end_edge_index:int = edges_of_face.index( end_edge_id )
    left_edge_index:int = edges_of_face.index( left_edge_id )
    right_edge_index:int = edges_of_face.index( right_edge_id )
    
    return start_edge_id, end_edge_id, left_edge_id, right_edge_id, start_edge_index, end_edge_index, left_edge_index, right_edge_index

def mesh_to_bmesh(mesh:bpy.types.Mesh) -> bpy.types.Mesh:
    if type( mesh ) is not bpy.types.Mesh:
        return None
    
    blender_mesh:bmesh = bmesh.new()
    blender_mesh.from_mesh(mesh)
    
    return blender_mesh

def delete_bmesh(blender_mesh:bmesh.types.BMesh) -> bool:
    if type( blender_mesh ) is not bmesh.types.BMesh:
        return False
    
    blender_mesh.free()
    
    return True

def bevel( blender_mesh:bmesh.types.BMesh, edge_ids_to_bevel:Array, offset_type:str = 'OFFSET', offset:float = 0.0, profile_type:str = 'SUPERELLIPSE', offset_pct:float = 0.0, segments:int = 1, profile:float = 0.5, affect:str = 'EDGES', clamp_overlap:bool = False, loop_slide:bool = True, mark_seam:bool = False, mark_sharp:bool = False, material:int = -1, harden_normals:str = False, face_strength_mode:str = 'NONE', miter_outer:str = 'SHARP', miter_inner:str = 'SHARP', spread:float = 0.1, vmesh_method:str = 'ADJ', release_confirm:bool = False, edge_selection_type:int = 3  ) -> Array | Array | Array | Array | Array | Array | Array:
    """
    Bevels the currently selected object and returns an array of the newly created faces

    Parameters
    ----------
        All parameters match those found in bpy.ops.mesh.bevel ( https://docs.blender.org/api/current/bpy.ops.mesh.html#bpy.ops.mesh.bevel ) excluding "edge_selection_type"
        edge_selection_type:int
            0 = orphaned edges only
            1 = full faces only (All edges form full faces and non are orphaned)
            2 = orphaned and full face (Do orphaned first)
            3 = orphaned and full face (Do full face first)
    
    Returns
    -------
        Array:
            An array of each bmesh created from a bevel operation (0-2 in length)
        An array of the newly created faces (Note: Sometimes their IDs can match previous face IDs from before the bevel was performed.)
    """
    
    if offset <= 0.0:
        offset = 0.1
    
    if offset_pct <= 0.0:
        offset_pct = 0.1
    
    if segments < 1:
        segments = 1
    
    if offset_type == 'PERCENT':
        offset = offset_pct
    
    beveled_blender_meshes:Array = []
    selected_faces:Array = []
    selected_face_indexes:Array = []
    selected_edges:Array = []
    selected_edge_indexes:Array = []
    selected_vertices:Array = []
    selected_vertex_indexes:Array = []
    
    selected_edge_objects:Array = []
    
    blender_mesh.edges.ensure_lookup_table()
    
    for edge_index in edge_ids_to_bevel:
        selected_edge_objects.append(blender_mesh.edges[edge_index])

    bevel_result:dict = bmesh.ops.bevel(
        blender_mesh,
        geom = selected_edge_objects,
        offset_type = offset_type,
        offset = offset,
        profile_type = profile_type,
        segments = segments,
        profile = profile,
        affect = affect,
        clamp_overlap = clamp_overlap,
        loop_slide = loop_slide,
        mark_seam = mark_seam,
        mark_sharp = mark_sharp,
        material = material,
        harden_normals = harden_normals,
        face_strength_mode = face_strength_mode,
        miter_outer = miter_outer,
        miter_inner = miter_inner,
        spread = spread,
        vmesh_method = vmesh_method
    )
    
    faces:Array = [[],[]]
    edges:Array = [[],[]]
    vertices:Array = [[], []]
    
    for face in bevel_result['faces']:
        faces[0].append(face)
        faces[1].append(face.index)
    
    selected_faces += faces[0]
    selected_face_indexes += faces[1]
    
    for edge in bevel_result['edges']:
        edges[0].append(edge)
        edges[1].append(edge.index)
    
    selected_edges += edges[0]
    selected_edge_indexes += edges[1]
    
    for vertex in bevel_result['verts']:
        vertices[0].append(vertex)
        vertices[1].append(vertex.index)
    
    selected_vertices += vertices[0]
    selected_vertex_indexes += vertices[1]
    
    beveled_blender_meshes.append(blender_mesh.copy())
    
    return beveled_blender_meshes, selected_faces, selected_face_indexes, selected_edges, selected_edge_indexes, selected_vertices, selected_vertex_indexes

def get_bounding_edges_of_face_groups( obj:bmesh.types.BMesh, faces:Array ) -> Array | Array | Array | Array:
    """
    Gets the outer and inner edges of every group of selected faces.

    Parameters
    ----------
    obj : bpy.types.Object
        The object with a bpy.types.Mesh that contains selected faces.

    Returns
    -------
        [0]
        An array of all the selected outer and inner edges separated into selection groups and loops within that selection group.
        [1]
        Same as zero, but contains the indexes of the edges instead of the MeshEdge objects
        [ ALL
            [ FACE SELECTION GROUP 1
                [ OUTER EDGES
                    bpy.types.MeshEdge,
                    ...
                ],
                [ INNER EDGES 1
                    bpy.types.MeshEdge,
                    ...
                ],
                [ INNER EDGES 2
                    bpy.types.MeshEdge,
                    ...
                ],
                ... EDGE n
            ],
            [ FACE SELECTION GROUP 2
                [ OUTER EDGES
                    bpy.types.MeshEdge,
                    ...
                ],
                [ INNER EDGES 1
                    bpy.types.MeshEdge,
                    ...
                ],
                [ INNER EDGES 2
                    bpy.types.MeshEdge,
                    ...
                ],
                ... EDGE n
            ],
            ... FACE SELECTION GROUP n
        ]
        [2]
        An array of all the selected outer and inner edges. These are not separated into groups but are, instead, just a one dimensional array of all the inner and outer edges.
        [3]
        Same as 2, but contains the indexes of the edges instead of the MeshEdge objects
    """
    face_groups:Array = get_grouped_faces( obj, faces )
    
    bounding_edges:Array = []
    
    processed_faces:Array = []
    processed_edges:Array = []
    
    for face_group_index, face_group in enumerate(face_groups):
        bounding_edges.append([])
        for face in face_group:
            if not face in processed_faces:
                processed_faces.append(face)
                
                for edge in obj.faces[face].edges:
                    if not edge.index in processed_edges:
                        processed_edges.append(edge.index)
                        
                        edges_faces = get_faces_of_edge_bmesh( obj, edge.index, 1, faces )[0]
                        
                        if len(edges_faces) == 1:
                            bounding_edges[ face_group_index ].append( edge )
    
    bounding_edges_grouped:Array = []
    bounding_edges_grouped_index:Array = []
    processed_edges:Array = []
    
    bounding_edges_1d:Array = []
    bounding_edges_1d_indexes:Array = []
    
    for bounding_edges_index, bounding_edges_group in enumerate( bounding_edges ):
        bounding_edges_grouped.append([])
        bounding_edges_grouped_index.append([])
        unprocessed_linked_edges:Array = []
        bounding_edges_sub_group:int = -1
        add_new_sub_group:bool = True
        
        while len(bounding_edges_group) != 0:
            unprocessed_edge = bounding_edges_group.pop()
            
            if add_new_sub_group:
                bounding_edges_sub_group += 1
                bounding_edges_grouped[ bounding_edges_index ].append([])
                bounding_edges_grouped[ bounding_edges_index ][ bounding_edges_sub_group ] = []
                bounding_edges_grouped_index[ bounding_edges_index ].append([])
                bounding_edges_grouped_index[ bounding_edges_index][ bounding_edges_sub_group ] = []
                add_new_sub_group = False
            
            if unprocessed_edge not in processed_edges:
                unprocessed_linked_edges.append( unprocessed_edge )
            
            while len( unprocessed_linked_edges ) != 0:
                add_new_sub_group = True
                processing_edge = unprocessed_linked_edges.pop()
                processed_edges.append( processing_edge )
                bounding_edges_grouped[ bounding_edges_index ][ bounding_edges_sub_group ].append( processing_edge )
                bounding_edges_grouped_index[ bounding_edges_index ][ bounding_edges_sub_group ].append( processing_edge.index )
                bounding_edges_1d.append( processing_edge )
                bounding_edges_1d_indexes.append( processing_edge.index )
                
                for index, edge in enumerate( bounding_edges_group ):
                    if edge.verts[0] == processing_edge.verts[0] or edge.verts[1] == processing_edge.verts[1] or edge.verts[1] == processing_edge.verts[0] or edge.verts[0] == processing_edge.verts[1]:
                        if edge not in processed_edges:
                            unprocessed_linked_edges.append( edge )
                        
                        bounding_edges_group.pop( index )
    
    return bounding_edges_grouped, bounding_edges_grouped_index, bounding_edges_1d, bounding_edges_1d_indexes

def object_exists(object_name:str = '') -> bool:
    for obj in bpy.context.scene.objects:
        if obj.name == object_name:
            return True
    
    return True

#TODO: THIS IS WAY TOO SLOW! For the love of god optimize this.
def get_grouped_faces( obj, face_indexes:Array ) -> Array:
    """
    Groups all of the faces on obj passed in by face_indexes. every face island inside of face_indexes is considered a group.
    
    Parameters
    ----------
    obj : bpy.types.Object
        The object with a bpy.types.Mesh that contains selected faces.
    face_indexes: Array
            A list of the face IDs you wish to group.
    
    Returns
    -------
        An array of all the faces grouped into islands.
        [
            [ FACE GROUP 1
                FACE ID1,
                FACE ID2,
                ...,
                FACE IDN
            ],
            [ FACE GROUP 2
                FACE ID3,
                FACE ID4,
                ...,
                FACE IDN
            ],
        ]
    """
    obj.faces.ensure_lookup_table()
    obj.edges.ensure_lookup_table()
    
    face_groups:Array = []
    face_queue:Array = []
    processed_faces:Array = []
    group_index:int = 0
    
    #Loop through all the faces
    for index in face_indexes:
        #Check if the face has already been processed, add it to the queue if not, ignore if it has.
        if not index in face_queue and index not in processed_faces:
            face_queue.append(index)
        
        #Add a new face group array if we've moved onto the next group or if this is the first group.
        if len(face_queue) > 0:
            face_groups.append([])
            group_index = len(face_groups) - 1
        
        face_queue_loop_index:int = 0
        
        #Loop through all the queued faces.
        while len(face_queue) > 0:
            face = face_queue[0]
            del face_queue[0]
            
            for edge in obj.faces[ face ].edges:
                faces_of_edge:Array = get_faces_of_edge_bmesh( obj, edge.index, 1, face_indexes)[1]
                
                for face_of_edge in faces_of_edge:
                    face_of_edge_index = face_of_edge
                    
                    if face_of_edge_index not in face_queue and face_of_edge_index not in processed_faces and face_of_edge_index != face:
                        face_queue.append(face_of_edge)
            
            #We add this face to the current face group
            face_groups[group_index].append(face)
            
            #We flag that this face has been processed already so that it can be skipped when we meet it again.
            processed_faces.append(face)
            
            face_queue_loop_index += 1
    
    for face_group in face_groups:
        face_group.sort()
    
    return face_groups

def getArmatureFromArmatureObject( armatureObject ):
    if type( armatureObject ) !=  bpy.types.Object:
        return None
    
    if not hasattr( armatureObject, 'data' ):
        return None
    
    armature = armatureObject.data
    
    if type( armature ) != bpy.types.Armature:
        return None
    
    return armature

def get_selected_vertices( obj:object ) -> Array | Array:
    bpy.ops.object.mode_set( mode = 'OBJECT', toggle = True )
    selectedVerticesIndexes = []
    selectedVertices = []
    
    if obj is not None and hasattr( obj.data, 'vertices' ) and len( obj.data.vertices ) > 0:
        my_selection = [ vertex for vertex in obj.data.vertices if vertex.select ]
        
        for vertex in my_selection:
            selectedVerticesIndexes.append( vertex.index )
            selectedVertices.append( vertex )
    
    return selectedVertices, selectedVerticesIndexes

#TODO: Change this to use a passed in object. Also wtf is the vertices parameter used for???
def createVertexGroup( name = 'Group' ):
    return bpy.context.selected_objects[0].vertex_groups.new( name = name )

#If a bone has the same tail and head position it's automatically deleted. This prevents that from happening.
def ensureBoneSurvival( bone ):
    if bone.head.x == bone.tail.x and bone.head.y == bone.tail.y and bone.head.z == bone.tail.z:
        bone.tail.z += 1.0

def get_selected_faces( blender_mesh:object ) -> Array | Array:
    selected_faces:Array = []
    selected_face_indexes:Array = []
    blender_mesh.select_flush(True)
    
    for face in blender_mesh.faces:
        if face.select:
            selected_faces.append( face )
            selected_face_indexes.append( face.index )
    
    return selected_faces, selected_face_indexes

def select_faces( obj:object, face_indexes:Array ):
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    
    for face_index in face_indexes:
        obj.data.polygons[ face_index ].select = True

#vertexIndex = the index of the vertex within obj. This is the safest way to query these values
def get_faces_connected_to_vertex( vertexIndex, obj ):
    if obj is None or not isType( obj, 'MESH' ) or not hasattr( obj, 'data' ):
        return []
    
    mesh = obj.data
    
    if type(mesh) != bpy.types.Mesh:
        return []
    
    triangles = []
    
    for face in mesh.polygons:
        for i in face.vertices:
            if i == vertexIndex:
                triangles.append( face )
                break
    
    return triangles

def isType( obj, typeString ):
    if hasattr( obj, 'type' ):
        return obj.type == typeString
    
    return False

def getCenterOfVertices( verticesArr ):
    vec = mathutils.Vector( (0.0, 0.0, 0.0) )
    
    howMany = 0
    
    for vertex in verticesArr:
        vec += vertex.co
        howMany += 1
    
    if howMany != 0:
        vec = vec / howMany
    
    return vec

#Takes all the selected vertices and calculates a normal based on the triangles connected to those vertices.
def calcNormalOfVertices( vertexIndexes = None, obj = None ):
    if vertexIndexes is None:
        vertexIndexes = []
    
    norms = []
    norm = mathutils.Vector( (0.0, 0.0, 0.0) )
    
    totalFaceCount = 0
    
    faces = []
    
    for vertexIndex in vertexIndexes:
        norms.append( mathutils.Vector( (0.0, 0.0, 0.0) ) )
        faces += get_faces_connected_to_vertex( vertexIndex, obj )
    
    highCount = 0
    highArray = []
    
    for face in faces:
        if highArray.count( face ) == 0:
            count = faces.count( face )
            if count > highCount:
                highArray = []
                highArray.append( face )
                highCount = count
            elif count == highCount:
                highArray.append( face )
    
    faces = highArray
    index = 0
    
    for vertexIndex in vertexIndexes:
        faceCount = len( faces )
        
        for face in faces:
            norms[ index ] += face.normal
            norm += face.normal
            totalFaceCount += 1
        
        if faceCount != 0:
            norms[ index ] = norms[ index ] / faceCount
        
        norms[ index ].normalize()
        
        index += 1
    
    if totalFaceCount != 0:
        norm = norm / totalFaceCount
    
    norm.normalize()
    
    return norm, norms

def getSelectedBone():
    bone = None
    bones = bpy.context.selected_editable_bones
    
    if bones is None:
        bones = bpy.context.selected_pose_bones
    
    if bones is not None and len( bones ) != 0:
        bone = bones[0]
    
    return bone

def deleteBoneWithName( boneName, armatureObject ):
    currentMode = None
    
    if bpy.context.object.mode != 'EDIT':
        currentMode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode = 'EDIT')
    
    armatureObject.data.edit_bones.remove( armatureObject.data.edit_bones[boneName] )

    if currentMode is not None:
        bpy.ops.object.mode_set( mode = currentMode )

def getVerticesFromVertexGroupName( obj, vertexGroupName ):
    return [ vert for vert in obj.data.vertices if obj.vertex_groups[ vertexGroupName ].index in [ i.group for i in vert.groups ] ]

def isBone( checkedObject ):
    varType = type( checkedObject )
    
    if checkedObject is not None or ( varType != bpy.types.Bone and varType != bpy.types.PoseBone and varType != bpy.types.EditBone and varType != bpy.types.ConstraintTargetBone ):
        return True
    
    return False

#pass in an armature object or armature and you will get the armature in return.
def getArmatureObjectsFromArmature( armature ):
    armatureType = type( armature )
    users = []
    
    if armatureType != bpy.types.Armature:
        if armatureType != bpy.types.Object:
            return None
        
        if not hasattr( armature, 'data' ):
            return None
        
        if type( armature.data ) != bpy.types.Armature:
            return None
        
        return [ armature ]
    
    for scene in bpy.data.scenes:
        for obj in scene.objects:
            if obj.data == armature:
                users.append( obj )
    
    if len( users ) == 0:
        return None
    
    return users

def getBonesArmature( bone ):
    if not isBone( bone ):
        return None, None
    
    armature = bone.id_data
    
    armatureObject = getArmatureObjectsFromArmature( armature )
    
    return armatureObject, armature

def get_selected_edges( obj:object ) -> Array | Array:
    mode:str = bpy.context.object.mode
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    mesh:bpy.types.Mesh = obj.data
    
    selected_edge_indexes:Array = []
    selected_edge_objects:Array = []
    
    if type( mesh ) == bpy.types.Mesh:
        selected_edge_objects = [ edge for edge in mesh.edges if edge.select ]
        
        edge_count = len( selected_edge_objects )
        
        selected_edge_indexes = [-1] * edge_count
        
        for selected_edge_object_index in range(0, edge_count):
            selected_edge_indexes[ selected_edge_object_index ] = selected_edge_objects[ selected_edge_object_index ].index
    
    bpy.ops.object.mode_set( mode = mode )
    
    return selected_edge_objects, selected_edge_indexes

def getBmeshSelectedEdges(bm):
    selectedEdgeIndexes = []
    selectedEdgeObjs = []
    edges = bm.edges
    
    for edge in edges:
        if edge.select:
            selectedEdgeIndexes.append(edge.index)
            selectedEdgeObjs.append(edge)
    
    return selectedEdgeObjs, selectedEdgeIndexes

def getObjectSelectedFaces( obj ) -> Array:
    selected_faces:Array = []
    
    if type( obj ) is bpy.types.Object:
        blender_mesh = mesh_to_bmesh(obj.data)
        
        selected_faces = getBmeshSelectedFaces( blender_mesh )
    
    return selected_faces

def getBmeshSelectedFaces(bm):
    selectedFaceIndexes = []
    selectedFaceObjs = []
    faces = bm.faces
    
    for face in faces:
        if face.select:
            selectedFaceIndexes.append(face.index)
            selectedFaceObjs.append(face)

    return selectedFaceObjs, selectedFaceIndexes

def getBoneVersionOfBoneFromName( boneName, armatureObject ):
    return armatureObject.data.bones[ boneName ]

def getPoseBoneVersionOfBoneFromName( boneName, armatureObject ):
    return armatureObject.pose.bones[ boneName ]

def getEditBoneVersionOfBoneFromName( boneName, armatureObject ):
    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.mode_set( mode = 'EDIT', toggle = True )
    
    return armatureObject.data.edit_bones[ boneName ]

def pair_edge_vertices( previous_bmesh:bmesh, previous_edge_id:int, connected_previous_edge_id:int, next_bmesh:bmesh, next_edge_id:int, connected_next_edge_id:int ) -> dict:
    """
    Pairs up vertices along two connected edges on two different mesh objects.
    
    Edges always have the same order (counter clockwise) on every face and seem to have the same starting point, but vertices are a different story. This solve the issue by mapping them back correctly.
    The edges need to be pre-calculated before passing them in, otherwise the mapping will be incorrect if you don't use mirrored edges between the two bmeshes.

    Parameters
    ----------
    previous_bmesh : bmesh
        The pre-bevel mesh
    
    previous_edge_id : int
        The first edge of the pre bevel mesh
    
    connected_previous_edge_id : int
        An edge connected to the previous_edge_id
    
    next_bmesh : bmesh
        The post bevel mesh. This MUST be a mesh created via a bevel from previous_mesh
    
    next_edge_id : int
        The first edge of the post bevel mesh. MUST map back to previous_edge_id
    
    connected_next_edge_id : int
        An edge connected to the next_edge_id. MUST map back to connected_previous_edge_id

    Returns
    -------
        A dict that contains the vertex IDs mapped onto each other ie: { previous_vertex_id : next_vertex_id }
    """
    pair_map:dict = {}
    previous_edge:bmesh.types.BMEdge = previous_bmesh.edges[ previous_edge_id ]
    connected_previous_edge:bmesh.types.BMEdge = previous_bmesh.edges[ connected_previous_edge_id ]
    
    next_edge:bmesh.types.BMEdge = next_bmesh.edges[ next_edge_id ]
    connected_next_edge:bmesh.types.BMEdge = next_bmesh.edges[ connected_next_edge_id ]
    
    #[0] = isolated vertex on previous, [1] = Overlapped vertex between previous and previous connected, [2] = isolated vertex on previous connected
    previous_vertex_map:Array = [0] * 3
    #[0] = isolated vertex on previous, [1] = Overlapped vertex between previous and previous connected, [2] = isolated vertex on previous connected
    next_vertex_map:Array = [0] * 3
    
    if previous_edge.verts[0] in connected_previous_edge.verts:
        previous_vertex_map[1] = previous_edge.verts[0].index
        previous_vertex_map[0] = previous_edge.verts[1].index
    else:
        previous_vertex_map[1] = previous_edge.verts[1].index
        previous_vertex_map[0] = previous_edge.verts[0].index
    
    if connected_previous_edge.verts[0] in previous_edge.verts:
        previous_vertex_map[2] = connected_previous_edge.verts[1].index
    else:
        previous_vertex_map[2] = connected_previous_edge.verts[0].index
    
    if next_edge.verts[0] in connected_next_edge.verts:
        next_vertex_map[1] = next_edge.verts[0].index
        next_vertex_map[0] = next_edge.verts[1].index
    else:
        next_vertex_map[1] = next_edge.verts[1].index
        next_vertex_map[0] = next_edge.verts[0].index
    
    if connected_next_edge.verts[0] in next_edge.verts:
        next_vertex_map[2] = connected_next_edge.verts[1].index
    else:
        next_vertex_map[2] = connected_next_edge.verts[0].index
    
    for index, previous in enumerate( previous_vertex_map ):
        pair_map[ previous ] = next_vertex_map[ index ]
    
    return pair_map

def get_edges_of_face_bmesh( blender_mesh:bmesh, face_index:int, select_state:int = 0, selected_edges:Array = [] ) -> Array | Array:
    edges_of_face:Array = []
    edges_of_face_indexes:Array = []
    
    blender_mesh.faces.ensure_lookup_table()
    if select_state == 0:
        for edge in blender_mesh.faces[ face_index ].edges:
            edges_of_face.append( edge )
            edges_of_face_indexes.append( edge.index )
    elif select_state == 1:
        for edge in blender_mesh.faces[ face_index ].edges:
            if edge.index in selected_edges:
                edges_of_face.append( edge )
                edges_of_face_indexes.append( edge.index )
    else:
        for edge in blender_mesh.faces[ face_index ].edges:
            if edge.index not in selected_edges:
                edges_of_face.append( edge )
                edges_of_face_indexes.append( edge.index )
    
    return edges_of_face, edges_of_face_indexes

def get_edges_of_face( obj:bpy.types.Object, face_index:int, select_state:int = 0 ) -> Array | Array:
    edges_of_face:Array = []
    edges_of_face_indexes:Array = []
    
    mesh = obj.data
    poly = obj.data.polygons[ face_index ]
    
    if select_state == 0:
        edges_of_face = [ mesh.edges[ mesh.loops[i].edge_index ] for i in poly.loop_indices ]
    elif select_state == 1:
        edges_of_face = [ mesh.edges[ mesh.loops[i].edge_index ] for i in poly.loop_indices if mesh.edges[ mesh.loops[i].edge_index ].select ]
    else:
        edges_of_face = [ mesh.edges[ mesh.loops[i].edge_index ] for i in poly.loop_indices if not mesh.edges[ mesh.loops[i].edge_index ].select ] 
    
    edge_count:int = len( edges_of_face )
    edges_of_face_indexes:Array = [0] * edge_count
    
    for index in range( 0, edge_count ):
        edges_of_face_indexes[ index ] = edges_of_face[ index ].index
        
    return edges_of_face, edges_of_face_indexes

def getPoseBoneVersionOfBone( bone ):
    if not isBone( bone ):
        return None
    
    boneName = bone.name
    armature = bone.id_data
    
    armatureObjects = getArmatureObjectsFromArmature( armature )
    
    if armatureObjects is None:
        return None
    
    return getPoseBoneVersionOfBoneFromName( boneName, armatureObjects[0] )

def ShowMessageBox( message = "", title = "Message Box", icon = 'INFO' ):
    def draw( self ):
        self.layout.label( text = message )
    
    bpy.context.window_manager.popup_menu( draw, title = title, icon = icon )

#https://blenderartists.org/t/extending-built-in-operator/1257955/4
def keywords_from_prop( p_rna ):
    kw = {}
    
    for kwname in ( "name", "description", "default", "min", "size", "max", "soft_min", "soft_max", "precision" ):
        value = getattr( p_rna, kwname, None )
        
        if value is not None:
            kw[ kwname ] = value
    
    if p_rna.type == 'ENUM':
        kw[ "items" ] = tuple( ( i.identifier, i.name, i.description ) for i in p_rna.enum_items )
    
    return kw

def props_from_op(idname):
    """
    Retrieves all the properties of a native Blender Operator. Useful for discovering how a native operator is laid out/designed.

    Parameters
    ----------
    idname : str
        The RNA id name of the operator. ex: 'mesh.bevel'

    Returns
    -------
        A dict that contains all the properties of the input operator rna id.
    """
    import _bpy
    
    props_dict = {}
    op_rna = _bpy.ops.get_rna_type( idname )
    
    for p in op_rna.properties:
        if p.identifier == "rna_type":
            continue
        
        prop = getattr( bpy.props, p.rna_type.identifier )
        kwargs = keywords_from_prop( p )
        props_dict[ p.identifier ] = prop, kwargs
    
    return props_dict
