#TODO: Write a function that normalizes the bone controllers: Deletes invalid bones, deletes unused constraints and keys, etc etc????
import bpy
from bpy.props import EnumProperty
from bpy.types import Operator, Panel
from bpy.utils import register_class, unregister_class

import mathutils
from mathutils import Euler

class SIMPLE_MORPH_219_PT_panel( Panel ):
    bl_idname = 'SIMPLE_MORPH_219_PT_panel'
    bl_label = 'Simple Morph 219'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    
    def draw( self, context ):
        selectedObject = None
        
        if len( context.selected_objects ) > 0:
            selectedObject = context.selected_objects[0]
        
        layout = self.layout
        
        createControllerBtn = layout.column()
        createControllerBtn.operator( 'simplemorph.219_op', text = 'Create Controller' ).action = 'CREATE_CONTROLLER'
        
        setDeformBtn = layout.column()
        setDeformBtn.operator( 'simplemorph.219_op', text = 'Set Deform' ).action = 'SET_DEFORM'
        
        freezeCopyBtn = layout.column()
        freezeCopyBtn.operator( 'simplemorph.219_op', text = 'Freeze Copy' ).action = 'FREEZE_COPY'
        
        compileBtn = layout.column()
        compileBtn.operator( 'simplemorph.219_op', text = 'Compile' ).action = 'COMPILE'
        
        decompileBtn = layout.column()
        decompileBtn.operator( 'simplemorph.219_decompile_op', text = 'Decompile' ).action = 'DECOMPILE'
        
        deleteControllerBtn = layout.column()
        deleteControllerBtn.operator( 'simplemorph.219_op', text = 'Delete Controller' ).action = 'DELETE_CONTROLLER'
        
        alignControllerBtn = layout.column()
        alignControllerBtn.operator( 'simplemorph.219_angle_controllers_op', text = 'Angle Controller' ).action = 'ALIGN_X_P'
        
        ResetVertexShapesKeyBtn = layout.column()
        ResetVertexShapesKeyBtn.operator( 'simplemorph.219_op', text = 'Reset Vertex Shapes' ).action = 'RESET_VERTEX_SHAPES'
        
        if context.object is None or context.object.mode != 'EDIT' or ( len( context.selected_objects ) == 0 or type( selectedObject ) != bpy.types.Object or selectedObject.type != 'MESH' ):
            createControllerBtn.enabled = False
        
        if context.object is None or ( context.object.mode != 'EDIT' and context.object.mode != 'POSE' ) or ( len( context.selected_objects ) == 0 or type( selectedObject ) != bpy.types.Object or selectedObject.type != 'ARMATURE' ):
            setDeformBtn.enabled = False
        
        if context.object is None or ( context.object.mode != 'EDIT' and context.object.mode != 'POSE' ) or ( len( context.selected_objects ) == 0 or type( selectedObject ) != bpy.types.Object or selectedObject.type != 'ARMATURE' ):
            deleteControllerBtn.enabled = False
        
        if context.object is None or ( context.object.mode != 'EDIT' and context.object.mode != 'POSE' ) or ( len( context.selected_objects ) == 0 or type( selectedObject ) != bpy.types.Object or selectedObject.type != 'ARMATURE' ):
            alignControllerBtn.enabled = False
        
        if context.object is None or context.object.mode != 'EDIT' or ( len( context.selected_objects ) == 0 or type( selectedObject ) != bpy.types.Object or selectedObject.type != 'MESH' ):
            ResetVertexShapesKeyBtn.enabled = False
        
        if context.object is None or context.object.mode != 'OBJECT' or ( len( context.selected_objects ) == 0 or type( selectedObject ) != bpy.types.Object or selectedObject.type != 'MESH' ):
            freezeCopyBtn.enabled = False
        
        if context.object is None or context.object.mode != 'OBJECT' or ( len( context.selected_objects ) == 0 or type( selectedObject ) != bpy.types.Object or selectedObject.type != 'MESH' ):
            compileBtn.enabled = False
        
        if context.object is None or context.object.mode != 'OBJECT' or ( len( context.selected_objects ) == 0 or type( selectedObject ) != bpy.types.Object or selectedObject.type != 'MESH' ):
            decompileBtn.enabled = False
    
    @staticmethod
    def getSelectedVertices( context ):
        return salowell_bpy_lib.getSelectedVertices()

class SIMPLE_MORPH_219_ANGLE_CONTROLLERS_op( Operator ):
    bl_idname = 'simplemorph.219_angle_controllers_op'
    bl_label = 'Simplemorph_219_op_label'
    bl_description = 'Simplemorph_219_op_description'
    bl_options = { 'REGISTER', 'UNDO' }
    
    action: EnumProperty(
        items = [
            ( 'ALIGN_X_P', 'align x +', 'align x +' ),
            ( 'ALIGN_X_M', 'align x -', 'align x -' ),
            ( 'ALIGN_Y_P', 'align y +', 'align y +' ),
            ( 'ALIGN_Y_M', 'align y -', 'align y -' ),
            ( 'ALIGN_Z_P', 'align z +', 'align z +' ),
            ( 'ALIGN_Z_M', 'align z -', 'align z -' ),
        ]
    )
    
    def execute( self, context ):
        direction = anchorTail = mathutils.Vector( (0.0, 0.0, 0.0) )
        
        if self.action == 'ALIGN_X_P':
            direction.x = 1.0
        elif self.action == 'ALIGN_X_M':
            direction.x = -1.0
        elif self.action == 'ALIGN_Y_P':
            direction.y = 1.0
        elif self.action == 'ALIGN_Y_M':
            direction.y = -1.0
        elif self.action == 'ALIGN_Z_P':
            direction.z = 1.0
        elif self.action == 'ALIGN_Z_M':
            direction.z = -1.0
            
        self.align_controller( context = context , direction = direction)
        
        return { 'FINISHED' }
    
    @staticmethod
    def align_controller( context , direction ):
        bone = salowell_bpy_lib.getSelectedBone()
        
        if bone == None:
            salowell_bpy_lib.ShowMessageBox( "You must select a bone first.", "Notice:", "ERROR" )
            return
        
        alignController( context, direction, bone)

class SIMPLE_MORPH_219_DECOMPILE_op( Operator ):
    bl_idname = 'simplemorph.219_decompile_op'
    bl_label = 'Simple Morph 219 Decompiler'
    bl_description = 'Simplemorph_219_op_description'
    bl_options = { 'REGISTER', 'UNDO' }
    
    action: EnumProperty(
        items = [
            ( 'DECOMPILE', 'decompile', 'decompile' ),
        ]
    )
    
    def execute( self, context ):
        selectedObject = context.selected_objects[0]
        salowell_bpy_lib.isolate_object_select( selectedObject )
        
        self.decompile( context, selectedObject )
        
        return { 'FINISHED' }
    
    @staticmethod
    def decompile( context, selectedObject ):
        startDecompile( context, selectedObject )

class SIMPLE_MORPH_219_op( Operator ):
    bl_idname = 'simplemorph.219_op'
    bl_label = 'Simplemorph_219_op_label'
    bl_description = 'Simplemorph_219_op_description'
    bl_options = { 'REGISTER', 'UNDO' }
    
    action: EnumProperty(
        items = [
            ( 'CREATE_CONTROLLER', 'clear scene', 'clear scene' ),
            ( 'DELETE_CONTROLLER', 'delete controller', 'delete controller' ),
            ( 'SET_DEFORM', 'set deform', 'set deform' ),
            ( 'FREEZE_COPY', 'freeze copy', 'freeze copy' ),
            ( 'COMPILE', 'compile', 'compile' ),
            ( 'RESET_VERTEX_SHAPES', 'reset vertex shapes', 'reset vertex shapes')
        ]
    )
    
    def execute( self, context ):
        if self.action == 'CREATE_CONTROLLER':
            self.create_controller( context = context )
        elif self.action == 'DELETE_CONTROLLER':
            self.delete_controller( context = context )
        elif self.action == 'SET_DEFORM':
            self.set_deform( context = context )
        elif self.action == 'FREEZE_COPY':
            self.freeze_copy( context = context )
        elif self.action == 'COMPILE':
            self.compile( context = context )
        elif self.action == 'RESET_VERTEX_SHAPES':
            self.reset_vertex_shapes( context = context )
        
        return { 'FINISHED' }
    
    @staticmethod
    def delete_controller( context ):
        startDeleteController( context )
    
    @staticmethod
    def create_controller( context ):
        startCreateController( context )
    
    @staticmethod
    def set_deform( context ):
        startSetDeform( context )
    
    @staticmethod
    def freeze_copy( context ):
        startFreezeCopy( context )
    
    @staticmethod
    def compile( context ):
        startCompile( context )
    
    @staticmethod
    def reset_vertex_shapes( context ):
        startResetVertexShapes( context )

classes = (SIMPLE_MORPH_219_PT_panel, SIMPLE_MORPH_219_op, SIMPLE_MORPH_219_ANGLE_CONTROLLERS_op, SIMPLE_MORPH_219_DECOMPILE_op)

register, unregister = bpy.utils.register_classes_factory(classes)

from SimpleMorph219 import salowell_bpy_lib

def register():
    pass

def unregister():
    pass

def alignController( context, direction, bone ):
    boneLength = 0.1
    bone = salowell_bpy_lib.getSelectedBone()
    
    if bone == None:
        return
    
    if isinstance(direction, mathutils.Vector) != True:
        return
    
    direction.normalize()
    direction *= boneLength
    
    armatureObject = salowell_bpy_lib.getArmatureObjectsFromArmature( bone.id_data )[0]
    
    anchorBone, reverserBone, baseBone, controllerBone = getAllBonesOfController( bone )
    
    anchorBone = salowell_bpy_lib.getEditBoneVersionOfBoneFromName( anchorBone.name, armatureObject )
    reverserBone = salowell_bpy_lib.getEditBoneVersionOfBoneFromName( reverserBone.name, armatureObject )
    baseBone = salowell_bpy_lib.getEditBoneVersionOfBoneFromName( baseBone.name, armatureObject )
    controllerBone = salowell_bpy_lib.getEditBoneVersionOfBoneFromName( controllerBone.name, armatureObject )
    
    anchorBone.tail = anchorBone.head + direction
    reverserBone.tail = reverserBone.head + direction
    baseBone.tail = baseBone.head + direction
    controllerBone.tail = controllerBone.head + direction

#TODO: If you have another armature selected while trying to create a controller it will cause some nice fun little bugs. FIX THIS.
#Create the armature on the passed in object if no armature exists
#Returns the existing or newly created armature as well as whether or not[boolean] a new armature had to be created.
def set_armature( object ):
    armature = None
    
    for child in object.children:
        armature = salowell_bpy_lib.getArmatureFromArmatureObject( child )
        
        if type( armature ) == bpy.types.Armature:
            break
        
        armature = None
    
    newArmature = False
    selectedObject = object
    armatureObject = None
    
    if armature == None:
        newArmature = True
        cont = bpy.context.area.type
        
        bpy.ops.object.mode_set( mode = 'OBJECT' )
        bpy.ops.object.armature_add( enter_editmode = False, align = 'WORLD', location = (0.0, 0.0, 0.0), scale = (1.0, 1.0, 1.0) )
        
        for armatureEntry in bpy.data.armatures:
            armatureEntrysObject = salowell_bpy_lib.getArmatureObjectsFromArmature( armatureEntry )
            #Again, we are only using the first object this armature is associated with. This plugin currently only uses a 1:1 link for armatures.
            if armatureEntrysObject != None and len( armatureEntrysObject ) > 0 and armatureEntrysObject[0].select_get():
                armatureObject = armatureEntrysObject[0]
                break
        
        armature = salowell_bpy_lib.getArmatureFromArmatureObject( armatureObject )
        armatureObject.parent = selectedObject
    else:
        armatureObject = salowell_bpy_lib.getArmatureObjectsFromArmature( armature )
        armatureObject = armatureObject[0]
    
    return armatureObject, armature, newArmature

#Creates all the bones needed for a controller point. No settings are applied here.
#Returns all 4 of the bones
def createControllerBones( armature, useExistingBone ):
    bpy.ops.object.mode_set( mode = 'EDIT' )
    
    editBones = armature.edit_bones
    
    if useExistingBone:
        anchorPoint = editBones[0]
        anchorPoint.name = 'anchor'
    else:
        anchorPoint = armature.edit_bones.new( 'anchor' )
    anchorPoint.tail.x = 0.0
    anchorPoint.tail.y = 0.0
    anchorPoint.tail.z = 1.0
    
    basePoint = armature.edit_bones.new( 'base' )
    basePoint.parent = anchorPoint
    basePoint.tail.x = 0.0
    basePoint.tail.y = 0.0
    basePoint.tail.z = 1.0
    
    controllerPoint = armature.edit_bones.new( 'controller' )
    controllerPoint.parent = basePoint
    controllerPoint.tail.x = 0.0
    controllerPoint.tail.y = 0.0
    controllerPoint.tail.z = 1.0
    
    reverserPoint = armature.edit_bones.new( 'reverser' )
    reverserPoint.parent = anchorPoint
    reverserPoint.tail.x = 0.0
    reverserPoint.tail.y = 0.0
    reverserPoint.tail.z = 1.0
    
    return anchorPoint, reverserPoint, basePoint, controllerPoint

def createController( theObject ):
    boneLength = 0.1
    selectedVerticesIndexes, selectedVertices = salowell_bpy_lib.getSelectedVertices()
    
    anchorHead = salowell_bpy_lib.getCenterOfVertices( selectedVertices )
    
    group = salowell_bpy_lib.createVertexGroup( selectedVerticesIndexes, 'Constraint' )
    group.add( selectedVerticesIndexes, 1.0, 'REPLACE' )
    
    armatureObject, armature, newArmature = set_armature( theObject )
    
    selectedObjects, selectedMode = salowell_bpy_lib.isolate_object_select( armatureObject )
    
    armature = armatureObject.data
    
    anchorPoint, reverserPoint, basePoint, controllerPoint = createControllerBones( armature, newArmature )
    
    anchorBoneName = anchorPoint.name
    reverserPointName = reverserPoint.name
    controllerPointName = controllerPoint.name
    basePointName = basePoint.name
    
    norm, vertexNorms = salowell_bpy_lib.calcNormalOfVertices( selectedVerticesIndexes, theObject )
    
    triangles = salowell_bpy_lib.get_triangles_connected_to_vertex( selectedVerticesIndexes[0], theObject )
    
    anchorTail = mathutils.Vector( (0.0, 0.0, 0.0) )
    anchorPoint.head = anchorHead
    anchorTail.x = anchorPoint.head.x
    anchorTail.y = anchorPoint.head.y
    anchorTail.z = anchorPoint.head.z
    anchorTail.x += norm.x * boneLength
    anchorTail.y += norm.y * boneLength
    anchorTail.z += norm.z * boneLength
    anchorPoint.tail = anchorTail
    salowell_bpy_lib.ensureBoneSurvival( anchorPoint )
    
    reverserPoint.head = anchorHead
    reverserPoint.tail = anchorTail
    salowell_bpy_lib.ensureBoneSurvival( reverserPoint )
    
    basePoint.head = anchorHead
    basePoint.tail = anchorTail
    salowell_bpy_lib.ensureBoneSurvival( basePoint )
    
    controllerPoint.head = anchorHead
    controllerPoint.tail = anchorTail
    salowell_bpy_lib.ensureBoneSurvival( controllerPoint )
    
    bpy.ops.object.mode_set( mode = 'POSE' )
    
    anchorPointPose = salowell_bpy_lib.getBoneVersionOfBoneFromName( anchorBoneName, armatureObject )
    anchorPointPose.hide = True
    
    reverserPointPose = salowell_bpy_lib.getBoneVersionOfBoneFromName( reverserPointName, armatureObject )
    reverserPointPose.hide = True
    
    basePointPose = salowell_bpy_lib.getBoneVersionOfBoneFromName( basePointName, armatureObject )
    basePointPose.hide = True
    
    armatureObject.pose.bones[ anchorBoneName ].constraints.new( 'COPY_LOCATION' )
    constraint = armatureObject.pose.bones[ anchorBoneName ].constraints[0]
    constraint.target = theObject
    constraint.subtarget = group.name
    
    armatureObject.pose.bones[ basePointName ].constraints.new( 'COPY_LOCATION' )
    constraint = armatureObject.pose.bones[ basePointName ].constraints[0]
    constraint.target = armatureObject
    constraint.subtarget = reverserPointName
    
    armatureObject.pose.bones[ controllerPointName ].constraints.new( 'COPY_LOCATION' )
    constraint = armatureObject.pose.bones[ controllerPointName ].constraints[0]
    constraint.target = armatureObject
    constraint.subtarget = anchorBoneName
    constraint.use_y = False
    constraint.target_space = 'LOCAL_WITH_PARENT'
    constraint.owner_space = 'LOCAL_WITH_PARENT'
    armatureObject.pose.bones[ controllerPointName ].lock_location[0] = True
    armatureObject.pose.bones[ controllerPointName ].lock_location[2] = True
    
    armatureObject.pose.bones[ reverserPointName ].constraints.new( 'COPY_LOCATION' )
    constraint = armatureObject.pose.bones[ reverserPointName ].constraints[0]
    constraint.target = armatureObject
    constraint.subtarget = anchorBoneName
    constraint.use_z = False
    constraint.target_space = 'POSE'
    constraint.owner_space = 'POSE'
    
    armatureObject.pose.bones[ reverserPointName ].constraints.new( 'COPY_LOCATION' )
    constraint = armatureObject.pose.bones[ reverserPointName ].constraints[1]
    constraint.target = armatureObject
    constraint.subtarget = controllerPointName
    constraint.use_x = False
    constraint.use_z = False
    constraint.invert_y = True
    constraint.target_space = 'LOCAL'
    constraint.owner_space = 'LOCAL'

#Pass in any bone from the controller hierarchy and it'll return the Anchor bone for that hierarchy.
def getBonesAnchorBone( bone ):
    anchorBone = None
    
    if bone == None or ( type( bone ) != bpy.types.PoseBone and type( bone ) != bpy.types.EditBone and type( bone ) != bpy.types.Bone ):
        return None
    
    anchorBone = bone
    
    while anchorBone.parent != None:
        anchorBone = anchorBone.parent
    
    return anchorBone

#Pass in any bone from the controller hierarchy and it'll return an array of all 4 bones [Anchor, Reverser, Base, Controller]
#It's not really perfect. If people start adding extra bones into the armature it could cause incorrect bones to be returned.
def getAllBonesOfController( bone ):
    anchorBone = getBonesAnchorBone(bone)
    reverserBone = None
    baseBone = None
    controllerBone = None
    
    if anchorBone != None:
        for tmpBone in anchorBone.children:
            if len( tmpBone.children ) > 0:
                baseBone = tmpBone
                controllerBone = baseBone.children[0]
            else:
                reverserBone = tmpBone
    
    return anchorBone, reverserBone, baseBone, controllerBone

#boneType: The type of bone that should be returned for the anchor bone
#boneType 0 = Bone
#boneType 1 = EditBone
#boneType 2 = PoseBone
def getAllAnchorBones( armatureObject, boneType = 0):
    anchorBones = []
    if type( armatureObject ) == bpy.types.Armature:
        armatureObject = salowell_bpy_lib.getArmatureObjectsFromArmature( armatureObject )[0]
    if type( armatureObject ) != bpy.types.Object and type( armatureObject.data ) != bpy.types.Armature:
        return None
    
    loopBoneType = None
    
    if boneType == 1:
        loopBoneType = armatureObject.data.edit_bones
    elif boneType == 2:
        loopBoneType = armatureObject.pose.bones
    else:
        loopBoneType = armatureObject.data.bones
    
    for bone in loopBoneType:
        if bone.parent == None:
            anchorBones.append( bone )
    
    return anchorBones

#Returns an array where each entry contains an array of length 4 representing the controller bones.
#Returns: [ [ anchorBone, reverserBone, baseBone, controllerBone ] ]
def getAllControllerBonesAsArrayHierarchy( armature ):
    anchorBones = getAllAnchorBones( armature, 1 )
    allBones = []
    
    if anchorBones == None or len( anchorBones ) == 0:
        return None
    
    for anchorBone in anchorBones:
        controllerBones = getAllBonesOfController( anchorBone )
        
        if controllerBones != None and len( controllerBones ) != 0:
            allBones.append( controllerBones )
    
    if len( allBones ) == 0:
        allBones = None
    
    return allBones

def startDeleteController( context ):
    bone = salowell_bpy_lib.getSelectedBone()
    
    if bone == None:
        salowell_bpy_lib.ShowMessageBox( "You must select a bone first.", "Notice:", "ERROR" )
        return
    
    anchorBone, reverserBone, baseBone, controllerBone = getAllBonesOfController( bone )
    
    armature = anchorBone.id_data
    armatureObject = salowell_bpy_lib.getArmatureObjectsFromArmature( armature )[0]
    
    if anchorBone != None:
        poseAnchorBone = salowell_bpy_lib.getPoseBoneVersionOfBone( anchorBone )
        
        poseConstraints = poseAnchorBone.constraints
        
        for constraint in poseConstraints:
            vertexGroup = None
            
            if constraint.subtarget in armatureObject.parent.vertex_groups:
                vertexGroup = armatureObject.parent.vertex_groups[ constraint.subtarget ]
            
            if vertexGroup != None:
                armatureObject.parent.vertex_groups.remove( vertexGroup )
        
        shapeKeyIndex = getShapeKeyIndexFromControllerBone( poseAnchorBone, armatureObject.parent )
        
        if shapeKeyIndex != None:
            armatureObject.parent.active_shape_key_index = shapeKeyIndex
            armatureObject.parent.shape_key_remove( armatureObject.parent.data.shape_keys.key_blocks[ shapeKeyIndex ] )
        
        salowell_bpy_lib.deleteBoneWithName( poseAnchorBone.name, armatureObject )
    
    if reverserBone != None:
        poseReverserBone = salowell_bpy_lib.getPoseBoneVersionOfBone( reverserBone )
        salowell_bpy_lib.deleteBoneWithName( poseReverserBone.name, armatureObject )
    
    if baseBone != None:
        poseBaseBone = salowell_bpy_lib.getPoseBoneVersionOfBone( baseBone )
        salowell_bpy_lib.deleteBoneWithName( poseBaseBone.name, armatureObject )
    
    if controllerBone != None:
        poseControllerBone = salowell_bpy_lib.getPoseBoneVersionOfBone( controllerBone )
        salowell_bpy_lib.deleteBoneWithName( poseControllerBone.name, armatureObject )

#Pass in any bone from a set of controllers (Anchor bone, base bone, reverser bone, or controller bone) and this will return the vertex group object along with the vertices that belong to that vertex group object of which the anchor bone uses to anchor itself relative to the object.
def getControllersVertexGroupVertices( bone ):
    anchorBone = getBonesAnchorBone( bone )
    poseBoneVersion = salowell_bpy_lib.getPoseBoneVersionOfBone( anchorBone )
    
    vertexGroupName = poseBoneVersion.constraints[0].subtarget
    
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    armatureObject, armature = salowell_bpy_lib.getBonesArmature( anchorBone )
#TODO: Currently defaulting to only the first object the Armature data block is being used by
    armatureObject = armatureObject[0]
    
    vertexGroup = armatureObject.parent.vertex_groups[ vertexGroupName ]
    verticesTmp = salowell_bpy_lib.getVerticesFromVertexGroupName( armatureObject.parent, vertexGroupName )
    
    vertices = []
    
    for vertex in verticesTmp:
        vertices.append(vertex)
    
    return vertexGroup, vertices

def startCreateController( context ):
    salowell_bpy_lib.isolate_object_select( context.edit_object )
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()
    selectedObject = context.selected_objects[0]
    
    if len( context.selected_objects ) > 0 and len( salowell_bpy_lib.getSelectedVertices()[0] ) > 0:
        createController( context.selected_objects[0] )
        salowell_bpy_lib.isolate_object_select( selectedObject )
        bpy.ops.object.mode_set( mode = 'EDIT' )
    elif selectedObject.type != 'MESH' and selectedObject.type != 'CURVE':
        salowell_bpy_lib.ShowMessageBox( "This operation can only be performed on a MESH or CURVE", "Notice:", "ERROR" )
    else:
        salowell_bpy_lib.ShowMessageBox( "You must select the vertices, edges, or faces that represent an anchor point for the controller you wish to create.", "Notice:", "ERROR" )

def setDeform( context, bone ):
    armature = None
    armatureObject = None
    parentObject = None
    bpy.ops.object.mode_set( mode = 'EDIT' )
    
    if type( bone ) != bpy.types.PoseBone:
        bone = bone.id_data.edit_bones[ bone.name ]
    elif type( bone ) != bpy.types.EditBone:
        bone = bone.id_data.data.edit_bones[ bone.name ]
    
    anchorBone, reverserBone, baseBone, controllerBone = getAllBonesOfController( bone )
    
    for scene in bpy.data.scenes:
        for object in scene.objects:
            if object.data == anchorBone.id_data:
                armature = object.data
                armatureObject = object
                parentObject = object.parent
                break
    
    allBonesHierarchy = getAllControllerBonesAsArrayHierarchy(armature)
    
    for controllerRow in allBonesHierarchy:
        contBone = salowell_bpy_lib.getPoseBoneVersionOfBoneFromName(controllerRow[3].name, armatureObject)
        anchorBone = salowell_bpy_lib.getPoseBoneVersionOfBoneFromName(controllerRow[0].name, armatureObject)
        
        contBone.location = anchorBone.location
    
    if parentObject.data.shape_keys == None or len( parentObject.data.shape_keys.key_blocks ) == 0:
        sk_basis = parentObject.shape_key_add( name = 'Basis' )
        sk_basis.interpolation = 'KEY_LINEAR'
        parentObject.data.shape_keys.use_relative = True
    
    shapeKeyIndex = getShapeKeyIndexFromControllerBone( controllerBone, parentObject )
    
    if shapeKeyIndex == None:
        shapeKey = parentObject.shape_key_add( name = 'Key' )
        shapeKey.interpolation = 'KEY_LINEAR'
        shapeKey.slider_max = 10.0
        shapeKey.slider_min = -10.0
        
        driver = shapeKey.driver_add( "value" )
        driver.driver.expression = 'var + 0.0'
        
        driverVariable = driver.driver.variables.new()
        driverVariable.type = 'TRANSFORMS'
        driverVariable.targets[0].id = armatureObject
        driverVariable.targets[0].transform_type = 'LOC_Y'
        driverVariable.targets[0].transform_space = 'LOCAL_SPACE'
        
        driverVariable.targets[0].bone_target = controllerBone.name
        
        shapeKeyIndex = getShapeKeyIndexFromControllerBone( controllerBone, parentObject )
    
    if shapeKeyIndex != None:
        parentObject.active_shape_key_index = shapeKeyIndex
        bpy.ops.object.mode_set( mode = 'OBJECT' )
        salowell_bpy_lib.isolate_object_select( parentObject )
        bpy.ops.object.mode_set( mode = 'EDIT' )
        parentObject.data.shape_keys.key_blocks[ shapeKeyIndex ].value = parentObject.data.shape_keys.key_blocks[ 'Basis' ].value

def getShapeKeyIndexFromControllerBone( bone, parentObject ):
    if parentObject.data.shape_keys.animation_data == None:
        return None
    
    anchorBone, reverserBone, baseBone, controllerBone = getAllBonesOfController( bone )
    shapeKeyIndex = None
    
    shapeKeysPathIds = []
    
    for shapeKey in parentObject.data.shape_keys.key_blocks:
        shapeKeysPathIds.append( shapeKey.path_from_id() + '.value' )
    
    for fCurve in parentObject.data.shape_keys.animation_data.drivers:
        if fCurve.driver.variables[0].targets[0].bone_target == controllerBone.name:
            if fCurve.data_path in shapeKeysPathIds:
                shapeKeyIndex = shapeKeysPathIds.index( fCurve.data_path )
                break
    
    return shapeKeyIndex

def startResetVertexShapes( context ):
    selectedObject = context.selected_objects[0]
    
    bpy.ops.object.mode_set( mode = 'OBJECT', toggle = True )
    
    selectedVerticesIndexes, selectedVertices = salowell_bpy_lib.getSelectedVertices()
    
    if bpy.context.active_object.active_shape_key != None and len( selectedVerticesIndexes ) != 0:
        bpy.ops.mesh.blend_from_shape( shape = 'Basis', blend = 1.0, add = False )
    
    salowell_bpy_lib.isolate_object_select( selectedObject )
    
    bpy.ops.object.mode_set( mode = 'EDIT', toggle = True )

def startFreezeCopy( context ):
    if len( context.selected_objects ) == 0:
        return
    
    parentObject = None
    selectedObject = context.selected_objects[0]
    
    if type( selectedObject ) == bpy.types.Object:
        for child in selectedObject.children:
            if type( child.data ) == bpy.types.Armature:
                parentObject = child
                break
    
    if parentObject == None:
        return
    
    salowell_bpy_lib.isolate_object_select( parentObject )
    parentObject.parent.select_set( True )
    bpy.ops.object.duplicate()
    
    newlyCreatedObject = None
    
    newObjects = []
    
    for newObject in bpy.context.selected_objects:
        if type( newObject.data ) != bpy.types.Armature:
            newlyCreatedObject = newObject
        
        newObjects.append( newObject )
    
    newlyCreatedObject.location = parentObject.location
    newlyCreatedObject.rotation_euler = parentObject.rotation_euler
    
    context.selected_objects[0].parent = parentObject.parent
    
    salowell_bpy_lib.isolate_object_select( selectedObject )
    
    for newObject in newObjects:
        newObject.hide_set( True )

def startCompile( context ):
    startFreezeCopy( context )
    selectedObject = context.selected_objects[0]
    salowell_bpy_lib.isolate_object_select( selectedObject )
    bpy.ops.object.convert( target = 'MESH' )
    
    armatureObject = None
    
    for child in selectedObject.children:
        childArmature = salowell_bpy_lib.getArmatureFromArmatureObject( child )
        
        if childArmature != None:
            armatureObject = child
            break
    
    if armatureObject != None:
        salowell_bpy_lib.isolate_object_select( armatureObject )
        bpy.ops.object.delete()
        salowell_bpy_lib.isolate_object_select( selectedObject )
    
    salowell_bpy_lib.unwrapObjectUV( selectedObject )

def startDecompile( context, selectedObject ):
    foundNewObject = False
    newObject = None
    newArmatureObject = None
    
    for child in selectedObject.children:
        if child.hide_get():
            newObject = child
            foundNewObject = True
            break
    
    if foundNewObject == False:
        salowell_bpy_lib.ShowMessageBox( "You must select an object that has been previously compiled by Simple Morph 219. (Object not found)", "Notice:", "ERROR" )
        return
    
    for child in newObject.children:
        newArmature = salowell_bpy_lib.getArmatureFromArmatureObject( child )
        
        if newArmature != None:
            newArmatureObject = child
            break
    
    if newArmatureObject == None:
        salowell_bpy_lib.ShowMessageBox( "You must select an object that has been previously compiled by Simple Morph 219. (Armature object not found)", "Notice:", "ERROR" )
        return
    
    newObject.hide_set( False )
    newArmatureObject.hide_set( False )
    
    newObject.parent = selectedObject.parent
    
    newObjectPosition = mathutils.Vector( (0.0, 0.0, 0.0) )
    newObjectPosition.x = selectedObject.location.x
    newObjectPosition.y = selectedObject.location.y
    newObjectPosition.z = selectedObject.location.z
    newObject.location = newObjectPosition
    
    newObjectRotation = Euler((0.0, 0.0, 0.0), 'XYZ')
    newObjectPosition.x = selectedObject.rotation_euler.x
    newObjectPosition.y = selectedObject.rotation_euler.y
    newObjectPosition.z = selectedObject.rotation_euler.z
    newObject.rotation_euler = newObjectPosition
    
    newObjName = selectedObject.name
    
    bpy.data.objects.remove( selectedObject, do_unlink = True )
    newObject.name = newObjName
    
    salowell_bpy_lib.isolate_object_select( newObject )

def startSetDeform( context ):
    selectedObject = None
    
    if len( context.selected_objects ) > 0:
        selectedObject = context.selected_objects[0]
    
    if type( selectedObject ) != bpy.types.Object:
        return
    
    if selectedObject.type != 'ARMATURE':
        return
    
    mode = bpy.context.object.mode
    
    salowell_bpy_lib.isolate_object_select( selectedObject )
    armatureParentObject = None
    
    for scene in bpy.data.scenes:
        for object in scene.objects:
            if object == selectedObject:
                armatureParentObject = object
                break
        
        if armatureParentObject != None:
            break
    
    if armatureParentObject == None:
        return
    
    bpy.ops.object.mode_set( mode = mode )
    bone = None
    
    if context.selected_pose_bones != None and len( context.selected_pose_bones ) > 0:
        bone = context.selected_pose_bones[0]
    
    if context.selected_bones != None and len( context.selected_bones ) > 0:
        bone = context.selected_bones[0]
    
    if bone == None:
        return
    
    setDeform( context = context, bone = bone )