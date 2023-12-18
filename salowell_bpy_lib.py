import bpy
from bpy.props import EnumProperty
from bpy.types import Operator, Panel
from bpy.utils import register_class, unregister_class

import mathutils

#Unselects all objects and then selects just the passed in Object
#Also returns the objects that were selected before this change is made along with the select mode.
def isolate_object_select( objectToIsolate ):
    selectedObjects = bpy.context.selected_objects
    selectedMode = None
    
    if bpy.context.object != None:
        selectedMode = bpy.context.object.mode
    
    bpy.context.view_layer.objects.active = objectToIsolate
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    bpy.ops.object.select_all( action = 'DESELECT' )
    objectToIsolate.select_set( True )
    
    return selectedObjects, selectedMode

def getArmatureFromArmatureObject( armatureObject ):
    if type( armatureObject ) !=  bpy.types.Object:
        return None
    
    if hasattr( armatureObject, 'data' ) != True:
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
def createVertexGroup( vertices, name = 'Group' ):
    return bpy.context.selected_objects[0].vertex_groups.new( name = name )

#If a bone has the same tail and head position it's automatically deleted. This prevents that from happening.
def ensureBoneSurvival( bone ):
    if bone.head.x == bone.tail.x and bone.head.y == bone.tail.y and bone.head.z == bone.tail.z:
        bone.tail.z += 1.0

#vertexIndex = the index of the vertex within obj. This is the safest way to query these values
def get_triangles_connected_to_vertex( vertexIndex, obj ):
    if obj == None or isType( obj, 'MESH' ) != True or hasattr( obj, 'data' ) != True:
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
def calcNormalOfVertices( vertexIndexes = [], obj = None ):
    norms = []
    norm = mathutils.Vector( (0.0, 0.0, 0.0) )
    
    totalFaceCount = 0
    
    faces = []
    faceCounter = []
    
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
    
    if bones == None:
        bones = bpy.context.selected_pose_bones
    
    if bones != None and len( bones ) != 0:
        bone = bones[0]
    
    return bone

def deleteBoneWithName( boneName, armatureObject ):
    currentMode = None
    
    if bpy.context.object.mode != 'EDIT':
        currentMode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode = 'EDIT')
    
    armatureObject.data.edit_bones.remove( armatureObject.data.edit_bones[boneName] )
   
    if currentMode != None:
       bpy.ops.object.mode_set( mode = currentMode )

def getVerticesFromVertexGroupName( object, vertexGroupName ):
    return [ vert for vert in object.data.vertices if object.vertex_groups[ vertexGroupName ].index in [ i.group for i in vert.groups ] ]

def isBone( checkedObject ):
    varType = type( checkedObject )
    
    if checkedObject != None or ( varType != bpy.types.Bone and varType != bpy.types.PoseBone and varType != bpy.types.EditBone and varType != bpy.types.ConstraintTargetBone ):
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
        
        if hasattr( armature, 'data' ) != True:
            return None
        
        if type( armature.data ) != bpy.types.Armature:
            return None
        
        return [ armature ]
    
    for scene in bpy.data.scenes:
        for object in scene.objects:
            if object.data == armature:
                users.append( object )
    
    if len( users ) == 0:
        return None
    
    return users

def getBonesArmature( bone ):
    if isBone( bone ) != True:
        return None, None
    
    armature = bone.id_data
    
    armatureObject = getArmatureObjectsFromArmature( armature )
    
    return armatureObject, armature

def getBoneVersionOfBoneFromName( boneName, armatureObject ):
    return armatureObject.data.bones[ boneName ]

def getPoseBoneVersionOfBoneFromName( boneName, armatureObject ):
    return armatureObject.pose.bones[ boneName ]

def getEditBoneVersionOfBoneFromName( boneName, armatureObject ):
    return armatureObject.data.edit_bones[ boneName ]

def getPoseBoneVersionOfBone( bone ):
    if isBone( bone ) != True:
        return None
    
    boneName = bone.name
    armature = bone.id_data
    
    armatureObjects = getArmatureObjectsFromArmature( armature )
    
    if armatureObjects == None:
        return None
    
    return getPoseBoneVersionOfBoneFromName( boneName, armatureObjects[0] )

def ShowMessageBox( message = "", title = "Message Box", icon = 'INFO' ):
    def draw( self, context ):
        self.layout.label( text = message )
    
    bpy.context.window_manager.popup_menu( draw, title = title, icon = icon )