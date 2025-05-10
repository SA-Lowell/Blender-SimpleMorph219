from __future__ import annotations
from ctypes import Array

import SimpleMorph219.layer_maps_lib_219, SimpleMorph219.realcorner219

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
    layer_maps = SimpleMorph219.layer_maps_lib_219.layer_maps_to_array(layer_maps)
    edge = edge_id
    
    real_corner_custom_prop_keys:Array = SimpleMorph219.realcorner219.get_all_real_corner_custom_prop_keys(blender_object)
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

def edge_reference_to_edges(edge_reference:Array, simple_morph_219_obj:SimpleMorph219.realcorner219.simple_morph_219_object, current_layer_prop_key_name:str) -> Array:
    real_corner_custom_prop_keys:Array = SimpleMorph219.realcorner219.get_all_real_corner_custom_prop_keys(bpy.data.objects[simple_morph_219_obj.object_name])
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
    from SimpleMorph219.realcorner219 import realCorner219PropName
    
    gen_real_corner_meshes_result:Array = gen_real_corner_meshes(blender_object, realCorner219PropName + str(dynamic_edge[3]))
    
    edge_ids = get_edges_from_dynamic_edge_fast(dynamic_edge, gen_real_corner_meshes_result[7], blender_object)
    
    return edge_ids

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
    layer_maps = SimpleMorph219.layer_maps_lib_219.layer_maps_to_array(layer_maps)
    
    edge_ids:Array = []
    layer_map:SimpleMorph219.layer_maps_lib_219.simple_morph_219_layer_map = layer_maps[dynamic_edge[3]]
    
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
    from SimpleMorph219.realcorner219 import realCorner219PropName
    
    layer_maps = SimpleMorph219.layer_maps_lib_219.layer_maps_to_array(layer_maps)
    
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
    from SimpleMorph219.realcorner219 import realCorner219PropName
    
    layer_maps = SimpleMorph219.layer_maps_lib_219.layer_maps_to_array(layer_maps)
    
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
                new_mapped_layer_edge_ids:Array = SimpleMorph219.layer_maps_lib_219.get_layer_map_edges_from_previous_layer_map_edge(layers_edge_id, current_layer_map_index - 1, layer_maps)
                
                for new_mapped_layer_edge_id in new_mapped_layer_edge_ids:
#TODO: Once again this [0] only retrieves the first result and ignores others. Eventually others need to be considered or perhaps not?????
                    current_layer_dynamic_edges.append(edge_to_edge_reference_bevel(new_mapped_layer_edge_id, layer_maps, blender_object, realCorner219PropName + str(current_layer_map_index))[0])
    
    seen = set()
    
    [x for x in layer_edge_ids if not (x in seen or seen.add(x))]
    
    return layer_edge_ids

def get_edges_from_dynamic_edge_fast(dynamic_edge:Array, layer_maps:Array, blender_object:object) -> Array:
    """
        Retrieves all of the edges that belong to the given dynamic_edge.
        This is different from get_edge_ids_from_dynamic_edge() as this function[get_edges_from_dynamic_edge_fast()] travels all the way down the layer_maps so it can determine all the edges that were dynamiclly generated and that technically should be included in this, whereas the other function only grabs the edges of this layer.
        NOTE: The layer index is determined by dynamic_edge[3]. This represents the layer at which the edges are selected/mapped to the dynamic edge. It's generally a layer below where the dynamic edges are saved.
        WARNING: consider using this function over get_edges_from_dynamic_edge(), as this one does not have to generate a full bevel map and all its meshes every time it runs.
        
        Parameters
        ----------
            dynamic_edge: Array
                The dynamic edge to use as a selection. See the return result of edge_to_edge_reference_bevel() for a reference on how this array is formatted.
            
            layer_maps: Array
                An array of simple_morph_219_layer_map objects. Must be in correct order.
        
        Returns
        -------
            edge_indexes: Array
                An array of all edge indexes
    """
    from SimpleMorph219.realcorner219 import realCorner219PropName
    
    layer_maps = SimpleMorph219.layer_maps_lib_219.layer_maps_to_array(layer_maps)
    
    edge_ids:Array = []
    
    high_index:int = dynamic_edge[3]
    low_edge_id:int = list(layer_maps[high_index].unbeveled_edges.values())[dynamic_edge[1]]
    
    layer_dynamic_edge = get_low_dynamic_edge_from_dynamic_edge(dynamic_edge, layer_maps, blender_object)
    
    low_edge_ids:Array = get_edge_ids_from_dynamic_edge(layer_dynamic_edge, layer_maps)
    
    layer_map_index:int = layer_dynamic_edge[3]
    
    loop_edge_ids:Array = low_edge_ids
    
    while layer_map_index < high_index:
        edge_ids:Array = []
        layer_map_index += 1
        
        for low_edge_id in loop_edge_ids:
            edge_id:int = layer_maps[layer_map_index].unbeveled_edges[low_edge_id]
            edge_ids.append(edge_id)
        
        loop_edge_ids = edge_ids
    
    return loop_edge_ids