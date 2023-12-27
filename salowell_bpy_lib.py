import random
import bpy
import mathutils

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
        lm = obj.data.uv_layers.new( name = 'UVMap' )
    
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

#Unselects all objects and then selects just the passed in Object
#Also returns the objects that were selected before this change is made along with the select mode.
def isolate_object_select( objectToIsolate ):
    selectedObjects = bpy.context.selected_objects
    selectedMode = None
    
    if bpy.context.object is not None:
        selectedMode = bpy.context.object.mode
    
    bpy.context.view_layer.objects.active = objectToIsolate
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    bpy.ops.object.select_all( action = 'DESELECT' )
    objectToIsolate.select_set( True )
    
    return selectedObjects, selectedMode

def getArmatureFromArmatureObject( armatureObject ):
    if type( armatureObject ) !=  bpy.types.Object:
        return None
    
    if not hasattr( armatureObject, 'data' ):
        return None
    
    armature = armatureObject.data
    
    if type( armature ) != bpy.types.Armature:
        return None
    
    return armature

def getSelectedVertices():
    bpy.ops.object.mode_set( mode = 'OBJECT', toggle = True )
    selectedVerticesIndexes = []
    selectedVertices = []
    
    if len( bpy.context.selected_objects ) > 0 and hasattr( bpy.context.selected_objects[0].data, 'vertices' ) and len( bpy.context.selected_objects[0].data.vertices ) > 0:
        my_selection = [ vertex for vertex in bpy.context.selected_objects[0].data.vertices if vertex.select ]
        
        for vertex in my_selection:
            selectedVerticesIndexes.append( vertex.index )
            selectedVertices.append( vertex )
    
    return selectedVerticesIndexes, selectedVertices

#TODO: Change this to use a passed in object. Also wtf is the vertices parameter used for???
def createVertexGroup( name = 'Group' ):
    return bpy.context.selected_objects[0].vertex_groups.new( name = name )

#If a bone has the same tail and head position it's automatically deleted. This prevents that from happening.
def ensureBoneSurvival( bone ):
    if bone.head.x == bone.tail.x and bone.head.y == bone.tail.y and bone.head.z == bone.tail.z:
        bone.tail.z += 1.0

#vertexIndex = the index of the vertex within obj. This is the safest way to query these values
def get_triangles_connected_to_vertex( vertexIndex, obj ):
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
        faces += get_triangles_connected_to_vertex( vertexIndex, obj )
    
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

#TESTED
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

def getBoneVersionOfBoneFromName( boneName, armatureObject ):
    return armatureObject.data.bones[ boneName ]

def getPoseBoneVersionOfBoneFromName( boneName, armatureObject ):
    return armatureObject.pose.bones[ boneName ]

def getEditBoneVersionOfBoneFromName( boneName, armatureObject ):
    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.mode_set( mode = 'EDIT', toggle = True )
    
    return armatureObject.data.edit_bones[ boneName ]

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
