from ctypes import Array
from enum import Enum

import random

import bpy
import bmesh
import mathutils

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
        mesh_2_face_shortest_distance_index:int = -1
        
        for mesh_2_face_center_index, mesh_2_face_center in enumerate( mesh_2_face_centers ):
            current_distance = ( mesh_1_face_center - mesh_2_face_center ).length
            
            if last_distance == -1:
                mesh_2_face_shortest_distance_index = mesh_2_face_center_index
            else:
                if current_distance < last_distance:
                    mesh_2_face_shortest_distance_index = mesh_2_face_center_index
            
            last_distance = current_distance
        
        paired_closest.append( [ mesh_1_face_indexes[ mesh_1_face_center_index ], mesh_2_face_indexes[ mesh_2_face_shortest_distance_index ] ] )
        
        del mesh_2_face_centers[ mesh_2_face_shortest_distance_index ]
    
    return paired_closest

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
        for face in mesh.faces:
            found_first = False
            
            if not face.index in owner_faces_indexes and face.index in selected_faces:
                for _, value in enumerate( face.verts ):
                    if value == mesh.edges[ edge ].verts[0] or value == mesh.edges[ edge ].verts[1]:
                        if found_first:
                            owner_faces.append( face )
                            owner_faces_indexes.append( face.index )
                            break
                        
                        found_first = True
    elif select_state == -1:
        for face in mesh.faces:
            found_first = False
            
            if not face.index in owner_faces_indexes and not face.index in selected_faces:
                for _, value in enumerate( face.verts ):
                    if value == mesh.edges[ edge ].verts[0] or value == mesh.edges[ edge ].verts[1]:
                        if found_first:
                            owner_faces.append( face )
                            owner_faces_indexes.append( face.index )
                            break
                        
                        found_first = True
    else:
        for face in mesh.faces:
            found_first = False
            
            if not face.index in owner_faces_indexes:
                for _, value in enumerate( face.verts ):
                    if value == mesh.edges[ edge ].verts[0] or value == mesh.edges[ edge ].verts[1]:
                        if found_first:
                            owner_faces.append( face )
                            owner_faces_indexes.append( face.index )
                            break
                        
                        found_first = True
    
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
    if edge_selection_type < 0:
        edge_selection_type = 0
    elif edge_selection_type > 3:
        edge_selection_type = 3
    
    if offset_type == 'PERCENT':
        offset = offset_pct
    
    beveled_blender_meshes:Array = []
    selected_faces:Array = []
    selected_face_indexes:Array = []
    selected_edges:Array = []
    selected_edge_indexes:Array = []
    selected_vertices:Array = []
    selected_vertex_indexes:Array = []
    
    orphaned_edges, faced_edges = separate_orphaned_and_faced_edges( blender_mesh, edge_ids_to_bevel) [0:2]
    
    has_orphaned_edges = True if len( orphaned_edges ) > 0 else False
    has_faced_edges = True if len( faced_edges ) > 0 else False
    
    if edge_selection_type == 0 and not has_orphaned_edges:
        return beveled_blender_meshes, selected_faces, selected_face_indexes, selected_edges, selected_edge_indexes, selected_vertices, selected_vertex_indexes
    elif edge_selection_type == 1 and not has_faced_edges:
        return beveled_blender_meshes, selected_faces, selected_face_indexes, selected_edges, selected_edge_indexes, selected_vertices, selected_vertex_indexes
    elif (edge_selection_type == 2 or edge_selection_type == 3) and not has_orphaned_edges and not has_faced_edges:
        return beveled_blender_meshes, selected_faces, selected_face_indexes, selected_edges, selected_edge_indexes, selected_vertices, selected_vertex_indexes
    
    loops:int = 1
    
    if edge_selection_type == 0:
        edge_mode = 0
    elif edge_selection_type == 1:
        edge_mode = 1
    elif edge_selection_type == 2:
        edge_mode = 0
        loops = 2
    elif edge_selection_type == 3:
        edge_mode = 1
        loops = 2
    
    for i in range(loops):
        if i == 1 and edge_selection_type == 3:
            edge_mode = 0
        elif i == 1 and edge_selection_type == 2:
            edge_mode = 1
        
        edges_to_select:Array = []
        
        if edge_mode == 1:
            edges_to_select = faced_edges
        else:
            edges_to_select = orphaned_edges
        
        for edge_id in edges_to_select:
            blender_mesh.edges[edge_id].select = True
        
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
    face_groups:Array = get_grouped_selected_faces( obj, faces )
    
    bounding_edges:Array = []
    edge_key_edges = map_edge_keys_to_edges(obj, True)
    
    processed_faces:Array = []
    processed_edges:Array = []
    
    for face_group_index, face_group in enumerate(face_groups):
        bounding_edges.append([])
        for face in face_group:
            if not face in processed_faces:
                processed_faces.append(face)
                
                for edge_key in face.edges:
                    edge_key = (edge_key.verts[0].index, edge_key.verts[1].index)
                    edge = edge_key_edges[edge_key]
                    if not edge in processed_edges:
                        processed_edges.append(edge)
                        
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
def get_grouped_selected_faces( obj, selected_faces:Array ) -> Array:
    selected_face_groups:Array = []
    
    if type( obj ) is bmesh.types.BMesh:
        polygon_group_index:int = 0
        selected_face_groups.append([])
        
        if len( selected_faces ) > 0:
            edge_key_edges = map_edge_keys_to_edges(obj, True)
            
            polygons_completed:Array = []
            edge_keys_completed:Array = []
            
            for edge_key in  edge_key_edges :
                if not edge_key_edges[edge_key].index in edge_keys_completed:
                    start_new_group = False
                    edge_keys_completed.append(edge_key_edges[edge_key].index)
                    polygons:Array = get_faces_of_edge_bmesh( obj, edge_key_edges[edge_key].index, 0 )[0]
                    
                    while len(polygons) > 0:
                        polygon_index = polygons.pop()
                        
                        if polygon_index.index in selected_faces and not polygon_index in polygons_completed:
                            polygons_completed.append(polygon_index)
                            
                            for edge_key2 in polygon_index.edges:
                                edge_key2 = (edge_key2.verts[0].index, edge_key2.verts[1].index)
                                
                                if not edge_key_edges[ edge_key2 ].index in edge_keys_completed:
                                    edge_keys_completed.append(edge_key_edges[ edge_key2 ].index)
                                    polygons2:Array = get_faces_of_edge_bmesh( obj, edge_key_edges[ edge_key2 ].index, 0 )[0]
                                    
                                    for polygon_index2 in polygons2:
                                        if polygon_index2.index in selected_faces and not polygon_index2.index in polygons_completed and not polygon_index2 in polygons :
                                            polygons.append(polygon_index2)
                                    
                                    if polygon_index.index in selected_faces and not polygon_index.index in selected_face_groups[polygon_group_index]:
                                        start_new_group = True
                                        selected_face_groups[polygon_group_index].append(polygon_index)
                    
                    if start_new_group:
                        polygon_group_index += 1
                        selected_face_groups.append([])
    
    selected_face_groups.pop()
    
    return selected_face_groups

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
