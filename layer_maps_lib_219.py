from ctypes import Array

import mathutils
import bmesh
import bpy

import SimpleMorph219.salowell_bpy_lib as salowell_bpy_lib, SimpleMorph219.realcorner219 as realcorner219

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

def get_selected_layer_index() -> int:
    return realcorner219.get_real_corner_custom_prop_key_index(bpy.context.selected_objects[0], bpy.context.scene.realCorner219Layers)

#TODO: If you order the pre-bevel edges by ID number (0-n), and then order the newly created bevel faces by id number (0-n), you can pair them up using these ordered values!!!!!.
#Do not try to dsetermine left and right based on largest and smallest faces in each row. The order can swap here.
def generate_bevel_layer_map(new_blender_mesh:bmesh.types.BMesh, previous_blender_mesh:bmesh.types.BMesh, new_bevel_face_ids_in:Array, previous_unbeveled_edge_ids_in:Array, bevel_segments:int) -> dict:
    previous_unbeveled_edge_ids_in = list(set(previous_unbeveled_edge_ids_in))
    bounding_edge_ids = salowell_bpy_lib.get_bounding_edges_of_face_groups(new_blender_mesh, new_bevel_face_ids_in)[3]
    layer_map:simple_morph_219_layer_map = simple_morph_219_layer_map()
    layer_map.set_empty()
    layer_map.blender_mesh = new_blender_mesh.copy()
    layer_map.previous_selected_edges = previous_unbeveled_edge_ids_in.copy()
    layer_map.previous_blender_mesh = previous_blender_mesh.copy()

    new_bevel_face_ids_ordered:Array = new_bevel_face_ids_in.copy()
    new_bevel_face_ids_ordered.sort()
    
    #This variable is a copy of the new faces but without the terminator faces. The terminator faces are *always* the lower bounds of new face IDs, while the actual columns that were formed from the previous edge are always the upper bounds of the IDs.
    non_terminator_start_index:int = len(new_bevel_face_ids_in) - (bevel_segments * len(previous_unbeveled_edge_ids_in))
    new_bevel_face_ids_ordered_without_terminators:Array = new_bevel_face_ids_ordered[non_terminator_start_index:]
    
    new_bevel_terminator_and_corner_faces_grouped:Array = salowell_bpy_lib.get_grouped_faces(new_blender_mesh, new_bevel_face_ids_ordered[0:non_terminator_start_index])
    processed_new_bevel_terminator_and_corner_faces_grouped:Array = []
    
    previous_unbeveled_edge_ids_ordered:Array = previous_unbeveled_edge_ids_in.copy()
    previous_unbeveled_edge_ids_ordered.sort()
    
    previous_unbeveled_edge_ids_pathed = salowell_bpy_lib.order_edges_by_pathing(previous_blender_mesh, previous_unbeveled_edge_ids_in)
    
    for previous_unbeveled_edge_id in previous_unbeveled_edge_ids_pathed:
        layer_map.beveled_faces_to_last_edge[previous_unbeveled_edge_id] = []
        layer_map.beveled_parallel_edges_to_last_edge[previous_unbeveled_edge_id] = []
        layer_map.beveled_startend_edges_to_last_edge[previous_unbeveled_edge_id] = []
        layer_map.beveled_leftright_edges_to_last_edge[previous_unbeveled_edge_id] = [[],[]]
    
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
    
    for previous_unbeveled_edge_id in previous_unbeveled_edge_ids_pathed:
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
        
        start_edge_id, end_edge_id, left_edge_id, right_edge_id = salowell_bpy_lib.get_left_right_start_end_edges_from_start_edge_id( new_blender_mesh, faces_of_column[0], parallel_starting_edge )[0:4]
        
        left_faces:Array = salowell_bpy_lib.get_faces_of_edge_bmesh( new_blender_mesh, left_edge_id, 1, new_bevel_face_ids_ordered )[1]
        right_faces:Array = salowell_bpy_lib.get_faces_of_edge_bmesh( new_blender_mesh, right_edge_id, 1, new_bevel_face_ids_ordered )[1]
        
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
            
            start_edge_id, end_edge_id, left_edge_id, right_edge_id = salowell_bpy_lib.get_left_right_start_end_edges_from_start_edge_id( new_blender_mesh, face_of_column, anchor_edge )[0:4]
            
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
        layer_map.beveled_startend_edges_to_last_edge[previous_unbeveled_edge_id] = [parallel_edges[0], parallel_edges[-1]]
        layer_map.beveled_leftright_edges_to_last_edge[previous_unbeveled_edge_id] = [left_edges, right_edges]
        
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
        
        layer_map.beveled_leftright_vertices_to_last_edge[previous_unbeveled_edge_id] = [left_vertices, right_vertices]
        
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
                            
                            vertex_face_group_edges:Array = salowell_bpy_lib.get_edges_from_faces(new_blender_mesh, vertex_face_group)
                            vertex_face_group_vertices:Array = salowell_bpy_lib.get_vertices_from_edges(new_blender_mesh, vertex_face_group_edges)
                            
                            layer_map.beveled_edges_to_last_vertex[previous_unbeveled_vertex] = vertex_face_group_edges
                            layer_map.beveled_vertices_to_last_vertex[previous_unbeveled_vertex] = vertex_face_group_vertices
                    
                    vertex_face_group_index += 1
            
            previous_unbeveled_vertex_index += 1
        
        processed_faces = processed_faces + faces_of_column
        index += 1
    
    previous_map:tuple = map_beveled_mesh_to_previous_layer(original_mesh = previous_blender_mesh, new_mesh = new_blender_mesh, new_faces = new_bevel_face_ids_in, new_layer_map = layer_map)
    layer_map.unbeveled_vertices = previous_map[0]
    layer_map.unbeveled_edges = previous_map[1]
    layer_map.unbeveled_faces = previous_map[2]
    
    return layer_map

def map_face_edges(original_mesh:bmesh, new_mesh:bmesh, original_face_id:int, new_face_id:int, layer_map:simple_morph_219_layer_map, new_edges_to_ignore:Array, original_edges_to_ignore:Array ) -> Array:
    """
    Maps all edges, of original_face_id from original_mesh onto new_face_id from _new_mesh. This operation skips over new_edgess_to_ignore from new_face_id and original_edges_to_ignore from new_mesh
    
    Parameters
    ----------
    original_mesh: bmesh
        The original mesh that contains the face original_face_id
    
    new_mesh: bmesh
        The new mesh that contains the face new_face_id
    
    original_face_id: int
        ID of the face from original_mesh
    
    new_face_id: int
        ID of the face from new_mesh
    
    layer_map: simple_morph_219_layer_map
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
        new_edge, distance = realcorner219.get_closest_edge(original_mesh, new_mesh, original_face_edge_id, new_face_edge_ids_tmp)
        
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

def map_beveled_mesh_to_previous_layer( original_mesh:bmesh, new_mesh:bmesh, new_faces:Array, new_layer_map:simple_morph_219_layer_map ) -> dict | dict | dict:
    """
    Maps all edges, vertices, and faces of new_mesh back to original_mesh. All vertices, edges, and faces that are part of the bevel operation are not included.
    
    Parameters
    ----------
    original_mesh: bmesh
        The pre-bevel mesh
    
    new_mesh: bmesh
        The post bevel mesh. This MUST be a mesh created via a bevel from previous_mesh
    
    new_faces: Array
        IDs of faces created from the bevel
    
    new_layer_map: simple_morph_219_layer_map
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
                
                closest_edge_id = realcorner219.get_closest_edge(original_mesh, new_mesh, original_mesh.faces[original_face].edges[0].index, new_mesh_edge_ids)
                
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