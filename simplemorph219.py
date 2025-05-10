#TODO: Write a function that normalizes the bone controllers: Deletes invalid bones, deletes unused constraints and keys, etc etc????
import bpy
from bpy.props import EnumProperty
from bpy.types import Operator, Panel, Object

import mathutils
import bmesh
import math

import SimpleMorph219.salowell_bpy_lib as salowell_bpy_lib, SimpleMorph219.realcorner219 as realcorner219

#Used to identify if this object  is a Simple Morph object.
simpleMorph219BaseName = 'simpleMorph219_Base'

classes = [ realcorner219.SIMPLE_MORPH_219_REAL_CORNER_PT_panel, realcorner219.SIMPLE_MORPH_219_REAL_CORNER_OPERATIONS ]
bpy.utils.register_classes_factory(classes)

def selected_array_curve_curve_219_poll(self, object):
    return object.type == 'CURVE'

bpy.types.Scene.selectedArrayCurveCurve219 = bpy.props.PointerProperty(
    type = bpy.types.Object,
    poll = selected_array_curve_curve_219_poll
)

bpy.types.Scene.selectedArrayCurveObject219 = bpy.props.PointerProperty(
    type = bpy.types.Object
)

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
        
        arrayCurve219Selector = layout.column()
        arrayCurve219Selector.prop_search(context.scene, "selectedArrayCurveCurve219", context.scene, "objects", text = 'Curve')
        
        arrayCurve219Selector = layout.column()
        arrayCurve219Selector.prop_search(context.scene, "selectedArrayCurveObject219", context.scene, "objects", text = 'Object')

        ResetVertexShapesKeyBtn = layout.column()
        ResetVertexShapesKeyBtn.operator( 'simplemorph.219_op', text = 'Make Array Curve 219' ).action = 'MAKE_ARRAY_CURVE_219'

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
        direction = mathutils.Vector( (0.0, 0.0, 0.0) )
        
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
            
        self.align_controller( direction = direction)
        
        return { 'FINISHED' }
    
    @staticmethod
    def align_controller( direction ):
        bone = salowell_bpy_lib.getSelectedBone()
        
        if bone is None:
            salowell_bpy_lib.ShowMessageBox( "You must select a bone first.", "Notice:", "ERROR" )
            return
        
        alignController( direction, bone )

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
        
        self.decompile( selectedObject )
        
        return { 'FINISHED' }
    
    @staticmethod
    def decompile( selectedObject ):
        startDecompile( selectedObject )

def calculate_point_on_line_at_distance(line_segment_start_point, line_segment_end_point, distance):
    direction_vector = line_segment_end_point - line_segment_start_point

    direction_vector.normalize()

    return line_segment_start_point + distance * direction_vector

def is_point_on_line_segment(point, line_segment_start_point, line_segment_end_point, tmp_point_index, tmp_tile_count, tmp_point_path):
    epsilon:float = 0.0001
    point = mathutils.Vector((point.x, point.y, point.z, 1.0))
    line_segment_start_point = mathutils.Vector((line_segment_start_point.x, line_segment_start_point.y, line_segment_start_point.z, 1.0))
    line_segment_end_point = mathutils.Vector((line_segment_end_point.x, line_segment_end_point.y, line_segment_end_point .z, 1.0))

    line_segment_vector:mathutils.Vector = (line_segment_end_point - line_segment_start_point)
    line_segment_length:float = line_segment_vector.length
    line_segment_vector.normalize()

    PRelative = point - line_segment_start_point
    point_start_distance:float = PRelative.length
    point_end_distance:float = (point - line_segment_end_point).length

    if point_start_distance < epsilon or point_end_distance < epsilon:
        return True
    
    projection = PRelative.dot(line_segment_vector)
    closetttt = closest_point_on_line(point, line_segment_start_point, line_segment_end_point)
    
    PRelative.normalize()
    
    if (point - closetttt).length < epsilon:
        if (closetttt - line_segment_start_point).length <= line_segment_length and (closetttt - line_segment_end_point).length <= line_segment_length:
            return True
    
    return False

def closest_point_on_line_segment(point, line_start, line_end):
    point = mathutils.Vector((point.x, point.y, point.z, 1.0))
    line_start = mathutils.Vector((line_start.x, line_start.y, line_start.z, 1.0))
    line_end = mathutils.Vector((line_end.x, line_end.y, line_end .z, 1.0))
    line_direction = line_end - line_start

    point_vector = point - line_start

    dot_product = line_direction.dot(point_vector)

    line_length = line_direction.length

    distance = dot_product / line_length

    if distance < 0:
        return line_start
    elif distance > line_length:
        return line_end
    
    closest_point:mathutils.Vector = line_start + distance * line_direction
    
    return closest_point

def closest_point_on_line(point, line_start, line_end):
    point = mathutils.Vector((point.x, point.y, point.z, 1.0))
    line_start = mathutils.Vector((line_start.x, line_start.y, line_start.z, 1.0))
    line_end = mathutils.Vector((line_end.x, line_end.y, line_end .z, 1.0))
    line_direction = line_end - line_start
    line_direction.normalize()
    v = point - line_start
    d = line_direction.dot(v)

    return line_start + line_direction * d

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
            ( 'RESET_VERTEX_SHAPES', 'reset vertex shapes', 'reset vertex shapes'),
            ( 'MAKE_ARRAY_CURVE_219', 'Make Array Curve 219', 'Make Array Curve 219')
        ]
    )
    
    def execute( self, context ):
        epsilon:float = 0.000001
        if self.action == 'CREATE_CONTROLLER':
            self.create_controller( context = context )
        elif self.action == 'DELETE_CONTROLLER':
            self.delete_controller()
        elif self.action == 'SET_DEFORM':
            self.set_deform( context = context )
        elif self.action == 'FREEZE_COPY':
            self.freeze_copy( context = context )
        elif self.action == 'COMPILE':
            self.compile( context = context )
        elif self.action == 'RESET_VERTEX_SHAPES':
            self.reset_vertex_shapes( context = context )
        elif self.action == 'MAKE_ARRAY_CURVE_219':
            curve_point_1:mathutils.Vector = None
            curve_point_2:mathutils.Vector = None

            object_anchor_1_global:mathutils.Vector = None
            object_anchor_2_global:mathutils.Vector = None

            curve_anchor_point_1:mathutils.Vector = None
            curve_anchor_point_2:mathutils.Vector = None

            object_copy:bpy.types.Object = context.scene.selectedArrayCurveObject219.copy()
            object_copy.data = context.scene.selectedArrayCurveObject219.data.copy()
            object_copy.parent = context.scene.selectedArrayCurveObject219.parent
            context.collection.objects.link(object_copy)

            object_anchor_point_distance:float = (mathutils.Vector((object_copy['CurveArray219_1'][0], object_copy['CurveArray219_1'][1], object_copy['CurveArray219_1'][2], 1.0)) - mathutils.Vector((object_copy['CurveArray219_2'][0], object_copy['CurveArray219_2'][1], object_copy['CurveArray219_2'][2], 1.0))).length
            object_anchor_point_vector:mathutils.Vector = None
            tmp_tile_count = 1
            
            for spline in context.scene.selectedArrayCurveCurve219.data.splines:
                point_index:int = 0
                
                object_anchor_1_global = object_copy.matrix_world @ mathutils.Vector((object_copy['CurveArray219_1'][0], object_copy['CurveArray219_1'][1], object_copy['CurveArray219_1'][2], 1.0))
                object_anchor_2_global = object_copy.matrix_world @ mathutils.Vector((object_copy['CurveArray219_2'][0], object_copy['CurveArray219_2'][1], object_copy['CurveArray219_2'][2], 1.0))
                object_anchor_angle = mathutils.Vector((1.0, 0.0, 0.0, 1.0)).angle(object_anchor_2_global - object_anchor_1_global)
                
                if (object_anchor_2_global - object_anchor_1_global).y < 0:
                    object_anchor_angle = -object_anchor_angle
                
                object_copy.matrix_world.translation.x = spline.points[point_index].co.x
                object_copy.matrix_world.translation.y = spline.points[point_index].co.y
                object_copy.matrix_world.translation.z = spline.points[point_index].co.z
                bpy.context.view_layer.update()
                
                while point_index < len(spline.points):
                    point_is_on_line_segment:bool = False
                    loop_starting_point_index:int = point_index#The index at which we started testing for where the 2nd anchor point will be for this object. This is the same index as the line segment.
                    first_loop:bool = True
                    
                    while not point_is_on_line_segment and point_index < len(spline.points):
                        point = spline.points[point_index]
                        curve_point_1 = mathutils.Vector((point.co.x, point.co.y, point.co.z, 1.0))#The first point that defines the line segment on Curve

                        if point_index < len(spline.points) - 1:
                            curve_point_2 = spline.points[point_index + 1].co#The second point that defines the line segment on Curve
                        else:
                            curve_point_2 = spline.points[0].co
                        
                        curve_point_2 = mathutils.Vector((curve_point_2.x, curve_point_2.y, curve_point_2.z, 1.0))
                        
                        if curve_anchor_point_1 is None:
                            curve_anchor_point_1 = curve_point_1
                        else:
                            curve_anchor_point_1 = object_copy.matrix_world @ mathutils.Vector((object_copy['CurveArray219_2'][0], object_copy['CurveArray219_2'][1], object_copy['CurveArray219_2'][2], 1.0))
                        tmp_point_path:str = ''

                        if first_loop:
                            tmp_point_path = 'A'
                            point_on_line:mathutils.Vector = calculate_point_on_line_at_distance(curve_anchor_point_1, curve_point_2, object_anchor_point_distance)
                        else:
                            tmp_point_path = 'B'
                            closest_point:mathutils.Vector = closest_point_on_line(curve_anchor_point_1, curve_point_1, curve_point_2)
                            point_is_on_line_segment = is_point_on_line_segment(closest_point, curve_anchor_point_1, curve_point_2, point_index, tmp_tile_count, tmp_point_path)
                            
                            if point_is_on_line_segment:
                                tmp_point_path = 'C'

                                point_on_line:mathutils.Vector = calculate_point_on_line_at_distance(closest_point, curve_point_2, object_anchor_point_distance)
                            else:
                                if curve_anchor_point_1 == closest_point:
                                    tmp_point_path = 'D'
                                    point_on_line:mathutils.Vector = calculate_point_on_line_at_distance(curve_anchor_point_1, curve_point_2, object_anchor_point_distance)
                                else:
                                    tmp_point_path = 'E'
                                    side_a_b_length:float = (curve_anchor_point_1 - closest_point).length
                                    side_a_c_length:float = object_anchor_point_distance

                                    sqrtValue = (side_a_c_length * side_a_c_length) - (side_a_b_length * side_a_b_length)
                                    
                                    if sqrtValue < 0:
                                        sqrtValue = -sqrtValue
                                    
                                    side_b_c_length:float = math.sqrt(sqrtValue)
                                    
                                    point_on_line:mathutils.Vector = calculate_point_on_line_at_distance(closest_point, curve_point_2, side_b_c_length)
                        
                        point_is_on_line_segment = is_point_on_line_segment(point_on_line, curve_point_1, curve_point_2, point_index, tmp_tile_count, tmp_point_path)
                        
                        if point_is_on_line_segment:
                            curve_anchor_point_2 = point_on_line
                            curve_anchor_angle_vecor = point_on_line - curve_anchor_point_1
                            curve_anchor_angle = mathutils.Vector((1.0, 0.0, 0.0, 0.0)).angle(curve_anchor_angle_vecor)
                            if (curve_anchor_point_2 - curve_anchor_point_1).y < 0:
                                curve_anchor_angle = -curve_anchor_angle
                            amount_to_rotate = curve_anchor_angle - object_anchor_angle
                            
                            object_copy.rotation_euler = (0 + object_copy.rotation_euler.x, 0 + object_copy.rotation_euler.y, amount_to_rotate + object_copy.rotation_euler.z)
                            bpy.context.view_layer.update()

                            object_anchor_1_global = object_copy.matrix_world @ mathutils.Vector((object_copy['CurveArray219_1'][0], object_copy['CurveArray219_1'][1], object_copy['CurveArray219_1'][2], 1.0))
                            move_direction = object_anchor_1_global - curve_anchor_point_1
                            object_copy.matrix_world.translation.x -= move_direction.x
                            object_copy.matrix_world.translation.y -= move_direction.y
                            object_copy.matrix_world.translation.z -= move_direction.z
                            bpy.context.view_layer.update()

                            previous_object:bpy.types.Object = object_copy.copy()
                            previous_object.data = object_copy.data.copy()
                            object_copy = previous_object
                            object_copy.data = previous_object.data
                            object_copy.parent = previous_object.parent
                            context.collection.objects.link(object_copy)

                            bpy.context.view_layer.update()

                            object_copy.name = 'a'

                            object_anchor_1_global = object_copy.matrix_world @ mathutils.Vector((object_copy['CurveArray219_1'][0], object_copy['CurveArray219_1'][1], object_copy['CurveArray219_1'][2], 1.0))
                            object_anchor_2_global = object_copy.matrix_world @ mathutils.Vector((object_copy['CurveArray219_2'][0], object_copy['CurveArray219_2'][1], object_copy['CurveArray219_2'][2], 1.0))
                            object_anchor_angle =  mathutils.Vector((1.0, 0.0, 0.0, 1.0)).angle(object_anchor_2_global - object_anchor_1_global)

                            if (object_anchor_2_global - object_anchor_1_global).y < 0:
                                object_anchor_angle = -object_anchor_angle
                            tmp_tile_count += 1
                        else:
                            point_index += 1
                        
                        first_loop = False
        
        return { 'FINISHED' }
    
    @staticmethod
    def delete_controller():
        startDeleteController()
    
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

def alignController( direction, bone ):
    boneLength = 0.1
    bone = salowell_bpy_lib.getSelectedBone()
    
    if bone is None:
        return
    
    if not isinstance(direction, mathutils.Vector):
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
def set_armature( obj ):
    armature = None
    
    for child in obj.children:
        armature = salowell_bpy_lib.getArmatureFromArmatureObject( child )
        
        if type( armature ) == bpy.types.Armature:
            break
        
        armature = None
    
    newArmature = False
    selectedObject = obj
    armatureObject = None
    
    if armature is None:
        newArmature = True
        
        bpy.ops.object.mode_set( mode = 'OBJECT' )
        bpy.ops.object.armature_add( enter_editmode = False, align = 'WORLD', location = (0.0, 0.0, 0.0), scale = (1.0, 1.0, 1.0) )
        
        for armatureEntry in bpy.data.armatures:
            armatureEntrysObject = salowell_bpy_lib.getArmatureObjectsFromArmature( armatureEntry )
            #Again, we are only using the first object this armature is associated with. This plugin currently only uses a 1:1 link for armatures.
            if armatureEntrysObject is not None and len( armatureEntrysObject ) > 0 and armatureEntrysObject[0].select_get():
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
    armatureObject = salowell_bpy_lib.getArmatureObjectsFromArmature( armature )[0]
    salowell_bpy_lib.isolate_object_select( armatureObject )
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
    selectedVertices, selectedVerticesIndexes = salowell_bpy_lib.get_selected_vertices( theObject )
    
    anchorHead = salowell_bpy_lib.getCenterOfVertices( selectedVertices )
    
    group = salowell_bpy_lib.createVertexGroup( 'Constraint' )
    group.add( selectedVerticesIndexes, 1.0, 'REPLACE' )
    
    armatureObject, armature, newArmature = set_armature( theObject )
    
    armature = armatureObject.data
    
    anchorPoint, reverserPoint, basePoint, controllerPoint = createControllerBones( armature, newArmature )
    
    anchorBoneName = anchorPoint.name
    reverserPointName = reverserPoint.name
    controllerPointName = controllerPoint.name
    basePointName = basePoint.name
    
    norm = salowell_bpy_lib.calcNormalOfVertices( selectedVerticesIndexes, theObject )[0]
    
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
    
    if bone is None or ( type( bone ) != bpy.types.PoseBone and type( bone ) != bpy.types.EditBone and type( bone ) != bpy.types.Bone ):
        return None
    
    anchorBone = bone
    
    while anchorBone.parent is not None:
        anchorBone = anchorBone.parent
    
    return anchorBone

#Pass in any bone from the controller hierarchy and it'll return an array of all 4 bones [Anchor, Reverser, Base, Controller]
#It's not really perfect. If people start adding extra bones into the armature it could cause incorrect bones to be returned.
def getAllBonesOfController( bone ):
    anchorBone = getBonesAnchorBone(bone)
    reverserBone = None
    baseBone = None
    controllerBone = None
    
    if anchorBone is not None:
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
        if bone.parent is None:
            anchorBones.append( bone )
    
    return anchorBones

#Returns an array where each entry contains an array of length 4 representing the controller bones.
#Returns: [ [ anchorBone, reverserBone, baseBone, controllerBone ] ]
def getAllControllerBonesAsArrayHierarchy( armature ):
    anchorBones = getAllAnchorBones( armature, 1 )
    allBones = []
    
    if anchorBones is None or len( anchorBones ) == 0:
        return None
    
    for anchorBone in anchorBones:
        controllerBones = getAllBonesOfController( anchorBone )
        
        if controllerBones is not None and len( controllerBones ) != 0:
            allBones.append( controllerBones )
    
    if len( allBones ) == 0:
        allBones = None
    
    return allBones

def startDeleteController():
    bone = salowell_bpy_lib.getSelectedBone()
    
    if bone is None:
        salowell_bpy_lib.ShowMessageBox( "You must select a bone first.", "Notice:", "ERROR" )
        return
    
    anchorBone, reverserBone, baseBone, controllerBone = getAllBonesOfController( bone )
    
    armature = anchorBone.id_data
    armatureObject = salowell_bpy_lib.getArmatureObjectsFromArmature( armature )[0]
    
    if anchorBone is not None:
        poseAnchorBone = salowell_bpy_lib.getPoseBoneVersionOfBone( anchorBone )
        
        poseConstraints = poseAnchorBone.constraints
        
        for constraint in poseConstraints:
            vertexGroup = None
            
            if constraint.subtarget in armatureObject.parent.vertex_groups:
                vertexGroup = armatureObject.parent.vertex_groups[ constraint.subtarget ]
            
            if vertexGroup is not None:
                armatureObject.parent.vertex_groups.remove( vertexGroup )
        
        shapeKeyIndex = getShapeKeyIndexFromControllerBone( poseAnchorBone, armatureObject.parent )
        
        if shapeKeyIndex is not None:
            armatureObject.parent.active_shape_key_index = shapeKeyIndex
            armatureObject.parent.shape_key_remove( armatureObject.parent.data.shape_keys.key_blocks[ shapeKeyIndex ] )
        
        salowell_bpy_lib.deleteBoneWithName( poseAnchorBone.name, armatureObject )
    
    if reverserBone is not None:
        poseReverserBone = salowell_bpy_lib.getPoseBoneVersionOfBone( reverserBone )
        salowell_bpy_lib.deleteBoneWithName( poseReverserBone.name, armatureObject )
    
    if baseBone is not None:
        poseBaseBone = salowell_bpy_lib.getPoseBoneVersionOfBone( baseBone )
        salowell_bpy_lib.deleteBoneWithName( poseBaseBone.name, armatureObject )
    
    if controllerBone is not None:
        poseControllerBone = salowell_bpy_lib.getPoseBoneVersionOfBone( controllerBone )
        salowell_bpy_lib.deleteBoneWithName( poseControllerBone.name, armatureObject )

#Pass in any bone from a set of controllers (Anchor bone, base bone, reverser bone, or controller bone) and this will return the vertex group object along with the vertices that belong to that vertex group object of which the anchor bone uses to anchor itself relative to the object.
def getControllersVertexGroupVertices( bone ):
    anchorBone = getBonesAnchorBone( bone )
    poseBoneVersion = salowell_bpy_lib.getPoseBoneVersionOfBone( anchorBone )
    
    vertexGroupName = poseBoneVersion.constraints[0].subtarget
    
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    armatureObject = salowell_bpy_lib.getBonesArmature( anchorBone )[0]
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
    
    if len( context.selected_objects ) > 0 and len( salowell_bpy_lib.get_selected_vertices( selectedObject )[1] ) > 0:
        createController( context.selected_objects[0] )
        salowell_bpy_lib.isolate_object_select( selectedObject )
        bpy.ops.object.mode_set( mode = 'EDIT' )
    elif selectedObject.type != 'MESH' and selectedObject.type != 'CURVE':
        salowell_bpy_lib.ShowMessageBox( "This operation can only be performed on a MESH or CURVE", "Notice:", "ERROR" )
    else:
        salowell_bpy_lib.ShowMessageBox( "You must select the vertices, edges, or faces that represent an anchor point for the controller you wish to create.", "Notice:", "ERROR" )

def setDeform( bone ):
    armature = None
    armatureObject = None
    parentObject = None
    bpy.ops.object.mode_set( mode = 'EDIT' )
    
    if type( bone ) != bpy.types.PoseBone:
        bone = bone.id_data.edit_bones[ bone.name ]
    elif type( bone ) != bpy.types.EditBone:
        bone = bone.id_data.data.edit_bones[ bone.name ]
    
    anchorBone, _, _, controllerBone = getAllBonesOfController( bone )
    
    for scene in bpy.data.scenes:
        for obj in scene.objects:
            if obj.data == anchorBone.id_data:
                armature = obj.data
                armatureObject = obj
                parentObject = obj.parent
                break
    
    allBonesHierarchy = getAllControllerBonesAsArrayHierarchy(armature)
    
    for controllerRow in allBonesHierarchy:
        contBone = salowell_bpy_lib.getPoseBoneVersionOfBoneFromName(controllerRow[3].name, armatureObject)
        anchorBone = salowell_bpy_lib.getPoseBoneVersionOfBoneFromName(controllerRow[0].name, armatureObject)
        
        contBone.location = anchorBone.location
    
    if parentObject.data.shape_keys is None or len( parentObject.data.shape_keys.key_blocks ) == 0:
        sk_basis = parentObject.shape_key_add( name = 'Basis' )
        sk_basis.interpolation = 'KEY_LINEAR'
        parentObject.data.shape_keys.use_relative = True
    
    shapeKeyIndex = getShapeKeyIndexFromControllerBone( controllerBone, parentObject )
    
    if shapeKeyIndex is None:
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
    
    if shapeKeyIndex is not None:
        parentObject.active_shape_key_index = shapeKeyIndex
        bpy.ops.object.mode_set( mode = 'OBJECT' )
        salowell_bpy_lib.isolate_object_select( parentObject )
        bpy.ops.object.mode_set( mode = 'EDIT' )
        parentObject.data.shape_keys.key_blocks[ shapeKeyIndex ].value = parentObject.data.shape_keys.key_blocks[ 'Basis' ].value

def getShapeKeyIndexFromControllerBone( bone, parentObject ):
    if parentObject.data.shape_keys.animation_data is None:
        return None
    
    controllerBone = getAllBonesOfController( bone )[3]
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
    
    selectedVerticesIndexes = salowell_bpy_lib.get_selected_vertices( selectedObject )[1]
    
    if bpy.context.active_object.active_shape_key is not None and len( selectedVerticesIndexes ) != 0:
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
    
    if parentObject is None:
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
        
        if childArmature is not None:
            armatureObject = child
            break
    
    if armatureObject is not None:
        salowell_bpy_lib.isolate_object_select( armatureObject )
        bpy.ops.object.delete()
        salowell_bpy_lib.isolate_object_select( selectedObject )
    
    salowell_bpy_lib.unwrapObjectUV( selectedObject )

def startDecompile( selectedObject ):
    foundNewObject = False
    newObject = None
    newArmatureObject = None
    
    for child in selectedObject.children:
        if child.hide_get():
            newObject = child
            foundNewObject = True
            break
    
    if foundNewObject is False:
        salowell_bpy_lib.ShowMessageBox( "You must select an object that has been previously compiled by Simple Morph 219. (Object not found)", "Notice:", "ERROR" )
        return
    
    for child in newObject.children:
        newArmature = salowell_bpy_lib.getArmatureFromArmatureObject( child )
        
        if newArmature is not None:
            newArmatureObject = child
            break
    
    if newArmatureObject is None:
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
    
    #TODO: Add random rotation to the UV
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
        for obj in scene.objects:
            if obj == selectedObject:
                armatureParentObject = obj
                break
        
        if armatureParentObject is not None:
            break
    
    if armatureParentObject is None:
        return
    
    bpy.ops.object.mode_set( mode = mode )
    bone = None
    
    if context.selected_pose_bones is not None and len( context.selected_pose_bones ) > 0:
        bone = context.selected_pose_bones[0]
    
    if context.selected_bones is not None and len( context.selected_bones ) > 0:
        bone = context.selected_bones[0]
    
    if bone is None:
        return
    
    setDeform( bone = bone )

def markObjectAsSimpleMorphBaseObject( obj ):
    obj[ simpleMorph219BaseName ] = True
    
    realcorner219.create_if_not_exists_simple_morph_219_object(obj.name) 

def isSimpleMorphBaseObject( obj ):
    if type( obj ) is not Object:
        return False
    
    return simpleMorph219BaseName in obj and type( obj[ simpleMorph219BaseName ] ) is bool and obj[ simpleMorph219BaseName ]

def isSimpleMorphTempBaseObject( obj ):
    if type( obj ) is not Object:
        return False
    
    return simpleMorph219BaseName in obj and type( obj[ simpleMorph219BaseName ] ) is bool and not obj[ simpleMorph219BaseName ]
