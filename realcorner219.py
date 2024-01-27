from enum import Enum

import bpy

from bpy.types import Operator, Panel
from bpy.props import ( BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty )
from bpy.utils import register_class, unregister_class

import bmesh

from . import salowell_bpy_lib, simplemorph219

realCorner219PropName = 'realCorner219_'

class realCorner219States(Enum):
    NONE = 0
    SELECTING_EDGE = 1
    UPDATING_LAYER = 2

realCorner219CurrentState = realCorner219States.NONE
realCorner219LastUpdate = []
realCorner219SelectedBaseObjName:str = ''
realCorner219ModifiedObjName:str = ''
realcorner219HandleSelectDeselectFunctionLocked:bool = False
update_real_corner_layer_values_locked:bool = False

def real_corner_changed_selected_layer( uiCaller, context ):
    pass

def update_real_corner_layer_values( op, context ):
    global update_real_corner_layer_values_locked, realCorner219CurrentState, realCorner219States, realCorner219LastUpdate
    
    #if update_real_corner_layer_values_locked:
        #return None
    
    objectNameToQueryPropertiesFrom:str = op.originalObjectName
    if realCorner219CurrentState == realCorner219States.UPDATING_LAYER and op.placeholderObjectName != '':
        objectNameToQueryPropertiesFrom = op.placeholderObjectName
    
    realCornerPropDict = realCornerPropStringToDict( bpy.data.objects[ objectNameToQueryPropertiesFrom ][ op.real_corner_layer_name ] )
    

    if realCorner219CurrentState != realCorner219States.UPDATING_LAYER:
#Here is where it goes wrong, this assignment to 'edges' is the problem... hmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm.
#It's fixed now but may need to change some of the design pattern... it very bad. bad bad. Me fuck dumb. Itchy tasty nuts
        realCornerPropDict[ 'edges' ] = selectedEdgesToCustomPropArray( bpy.data.objects[ op.originalObjectName ] )
    
    realCornerPropDict[ 'bevel_settings' ][ 'segments' ] = op.bevelSegments
    realCornerPropDict[ 'bevel_settings' ][ 'width' ] = op.bevelWidth
    
    realCorner219LastUpdate = [
        op.originalObjectName,
        op.real_corner_layer_name,
        realCornerPropDictToString( realCornerPropDict )
    ]
    
    return None

def update_real_corner_selection_list( scene, context ):
    items = []
    selectedObject = bpy.context.selected_objects
    
    if len( selectedObject ) > 0:
        selectedObject = selectedObject[0]
        
        realCornerKeys = getAllRealCornerCustomPropKeys( selectedObject )
        realCornerKeyLayer = 0
        
        for realCornerKey in realCornerKeys:
            realCornerKeyLayerStr = str( realCornerKeyLayer )
            items.append( ( realCornerKey, 'Layer ' + realCornerKeyLayerStr, 'Editing Real Corner layer ' + realCornerKeyLayerStr ) )
            realCornerKeyLayer += 1
    
    return items

def createRealCornerCustomPropKeyIfNoneExists( obj ):
    keyArray = getAllRealCornerCustomPropKeys( obj )
    
    if len( keyArray ) == 0:
        keyArray.append( createNewRealCornerCustomProperty( obj, realCorner219PropName ) )
    
    return keyArray

def getRealCornerCustomPropKeyIndex( obj, propKey):
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

def getAllRealCornerCustomPropKeys( obj ):
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

class SIMPLE_MORPH_219_REAL_CORNER_QuickOps( Operator ):
    bl_idname = 'realcorner219.real_corner_quickops_op'
    bl_label = 'Real Corner 219 - Quick Operators'
    bl_description = 'Simplemorph_219_op_description'
    
    action: EnumProperty(
        items = [
            ( "TEST", "Test", "Test" ),
            ( "APPLY_REAL_CORNER_CHANGES", "Apply Real Corner Changes", "This is used to apply any recent real corner changes that were made" ),
            ( "TURN_ON_EDGE_SELECT", "Turn On Real Corner 219 Edge Select", "Turns on the Real Corner 219 Edge Select mode."),
            ( "TURN_OFF_AND_SAVE_EDGE_SELECT", "Turn Off Real Corner 219 Edge Select and save", "Turns off the Real Corner 219 Edge Select mode and saves the currently selected edges."),
        ]
    )
    
    def execute( self, context ):
        global realCorner219CurrentState, realCorner219SelectedBaseObjName, realCorner219ModifiedObjName, realcorner219HandleSelectDeselectFunctionLocked
        
        if self.action == 'TEST':
            salowell_bpy_lib.get_bounding_edges_of_selected_face_groups( bpy.context.selected_objects[0] )
            
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

    bevelSegments: IntProperty(
        name = 'Segments (Bevel Segments)',
        default = 0,
        update = update_real_corner_layer_values,
        min = 0,
        soft_min = 0
    )
    
    bevelWidth: FloatProperty(
        default = 0.0,
        name = "Width (Bevel Width)",
        precision = 4,
        unit = "LENGTH",
        update = update_real_corner_layer_values
    )
    
    preview: BoolProperty(
        default = True,
        name = "Preview"
    )
    
    def draw( self, context ):
        layout = self.layout
        layout.label( text = 'Updating Layer ' + str( self.real_corner_layer_index ) )
        layout.prop( self, "preview" )
        layout.prop( self, "bevelSegments" )
        layout.prop( self, "bevelWidth" )

    def execute( self, context ):
        global realCorner219CurrentState, realCorner219SelectedBaseObjName, realCorner219ModifiedObjName, realcorner219HandleSelectDeselectFunctionLocked, update_real_corner_layer_values_locked
        
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
            self.bevelSegments = realCornerPropDict[ 'bevel_settings' ][ 'segments' ]
            self.bevelWidth = realCornerPropDict[ 'bevel_settings' ][ 'width' ]
            bpy.data.objects[ self.originalObjectName ][ self.real_corner_layer_name ] = realCornerPropDictToString( realCornerPropDict )
            
            bpy.ops.object.mode_set( mode = 'OBJECT')
            bpy.ops.object.duplicate()
            bpy.data.objects[ self.originalObjectName ].hide_viewport = True
            updatedObject = context.selected_objects[0]
            updatedObject[ simplemorph219.simpleMorph219BaseName ] = False
            salowell_bpy_lib.isolate_object_select( updatedObject )
            realCorner219ModifiedObjName = updatedObject.name
            genRealCornerMesh( updatedObject, self.real_corner_layer_name )
            self.placeholderObjectName = context.selected_objects[0].name
            realcorner219HandleSelectDeselectFunctionLocked = False
        else:
            realcorner219HandleSelectDeselectFunctionLocked = True
            update_real_corner_layer_values_locked = True
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
            
            genRealCornerMesh( updatedObject, self.real_corner_layer_name )
            self.placeholderObjectName = context.selected_objects[0].name
            realcorner219HandleSelectDeselectFunctionLocked = False
            update_real_corner_layer_values_locked = False
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
        
        testBtn = layout.column()
        testObj = testBtn.operator( 'realcorner219.real_corner_quickops_op', text = 'Test' )
        testObj.action = 'TEST'
        
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
            updateLayerObj.real_corner_layer_index = getRealCornerCustomPropKeyIndex( context.selected_objects[0], realCorner219LayerIndex )
            updateLayerObj.originalObjectName = selectedObject.name
            updateLayerObj.objectLayerBeingModified = context.scene.realCorner219Layers

    def execute( self, context ):
        bevelLayers = getAllRealCornerCustomPropKeys( context.selected_objects[0] )

        if len( bevelLayers ) == 0:
            keyName = createNewRealCornerCustomProperty( context.selected_objects[0], realCorner219PropName )
            bevelLayers.append( keyName )
        
        bevelSegments=3
        
        me = bpy.context.active_object.data
        bm:bmesh = bmesh.new()
        bm.from_mesh( me )
        
        iniSelEdgeObjs = salowell_bpy_lib.getBmeshSelectedEdges( bm )[0]
        #iniSelPolyObjs, iniSelPolyIndexes = salowell_bpy_lib.getBmeshSelectedFaces( bm )
        
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
    
    return salowell_bpy_lib.getMeshSelectedEdges( obj )[1]

def createEmptyRealCornerPropDict() -> dict:
    realCornerPropDict:dict = {}
    realCornerPropDict[ 'edges' ] = []
    realCornerPropDict[ 'bevel_settings' ] = {}
    realCornerPropDict[ 'bevel_settings' ][ 'segments' ]:int = 0
    realCornerPropDict[ 'bevel_settings' ][ 'width' ]:float = 0.0
    
    return realCornerPropDict

def realCornerPropDictToString( realCornerPropDict:dict ) -> str:
    realCornerPropString:str = '0(' + ','.join( str( edgeId ) for edgeId in realCornerPropDict[ 'edges' ] ) + ')'
    realCornerPropString = realCornerPropString + '(' + str( realCornerPropDict[ 'bevel_settings' ][ 'segments' ] ) + ',' + str( realCornerPropDict[ 'bevel_settings' ][ 'width' ] ) + ')'
    
    return realCornerPropString

def realCornerPropIndexToDict( obj:object, propKey:str ) -> dict:
    return realCornerPropStringToDict( obj[ propKey ] )

def realCornerPropStringToDict( realCornerPropString:str ) -> str:
    realCornerPropDict = createEmptyRealCornerPropDict()
    realCornerPropDict:dict = {}
    realCornerPropDict[ 'edges' ] = []
    realCornerPropDict[ 'bevel_settings' ] = {}
    realCornerPropDict[ 'bevel_settings' ][ 'segments' ]:int = 1
    realCornerPropDict[ 'bevel_settings' ][ 'width' ]:float = 0.001
    
    propertyValues = realCornerPropString.strip().lstrip( '0' ).lstrip( '(' ).rstrip( ')' ).split( ')(' )
    
    for index, value in enumerate( propertyValues ):
        split = value.split( ',' )
        

        
        if index == 0 and value != '':
            for edgeIndex, edgeValue in enumerate( split ):
                if edgeValue != '':
                    split[ edgeIndex ] = int( edgeValue )
            
            realCornerPropDict[ 'edges' ] = split
        elif index == 1 and value != '':
            realCornerPropDict[ 'bevel_settings' ][ 'segments' ] = realCornerPropDict[ 'bevel_settings' ][ 'segments' ] if len( split ) < 1 else int( split[0] )
            realCornerPropDict[ 'bevel_settings' ][ 'width' ]  = realCornerPropDict[ 'bevel_settings' ][ 'width' ] if len( split ) < 2 else float( split[1] )
    
    return realCornerPropDict

#This is currently a hacky solution for updating. I need to learn the correct design paradigm for Blender's API.
@bpy.app.handlers.persistent
def applyRealCornerUpdate( scene ) -> None:
    global realCorner219LastUpdate
    
    if len( realCorner219LastUpdate ) != 0:
        bpy.data.objects[ realCorner219LastUpdate[0] ][ realCorner219LastUpdate[1] ] = realCorner219LastUpdate[2]
        realCorner219LastUpdate = []

def genRealCornerMeshAtPrevIndex( obj, layerIndexKey ) -> None:
    propKeyIndex = getRealCornerCustomPropKeyIndex( obj, layerIndexKey )
    
    if propKeyIndex > 0:
        propKeyIndex -= 1
        PropKeysArr = getAllRealCornerCustomPropKeys( obj )
        genRealCornerMesh( obj, PropKeysArr[ propKeyIndex ] )

def genRealCornerMesh( obj, layerIndexKey ) -> None:
    realCornerPropKeys = getAllRealCornerCustomPropKeys( obj )
    layerIndex = getRealCornerCustomPropKeyIndex( obj, layerIndexKey )
    
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
        
        bpy.ops.object.mode_set( mode = 'EDIT')
        bpy.ops.mesh.bevel( offset_type = 'WIDTH', offset = propDic[ 'bevel_settings' ][ 'width' ], profile_type = 'SUPERELLIPSE', offset_pct = 0.0, segments = propDic[ 'bevel_settings' ][ 'segments' ], profile = 0.5, affect = 'EDGES', clamp_overlap = False, loop_slide = True, mark_seam = False, mark_sharp = False, material = -1, harden_normals = False, face_strength_mode = 'NONE', miter_outer = 'SHARP', miter_inner = 'SHARP', spread = 0.1, vmesh_method = 'ADJ', release_confirm = False )

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
            salowell_bpy_lib.isolate_object_select( bpy.data.objects[ realCorner219SelectedBaseObjName ] )

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
