import maya.cmds as cmds
import re
import math

created_parentConstraints = []
tPoseRotations = {}
lock_value_cache = {}


def select_target_root(*args):
    global target_root
    target_root = cmds.ls(selection=True, type='transform')

    if len(target_root) != 1:
        target_root = None
        cmds.textField('target_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message='Please select one root object for "target".', button='OK')
    else:
        cmds.textField('target_textField', edit=True, text=target_root[0])


def select_animated_root(*args):
    global animated_root
    animated_root = cmds.ls(selection=True, type='transform')

    if len(animated_root) != 1:
        animated_root = None
        cmds.textField('animated_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message='Please select one root object for "animated".', button='OK')
    else:
        cmds.textField('animated_textField', edit=True, text=animated_root[0])


def get_transform_of_shape(relative):
    transform_node = cmds.listRelatives(relative, parent=True)
    return transform_node[0]


def cache_locks(objects):
    for object in objects:
        lockX = cmds.getAttr(object + '.rotateX', lock=True)
        lockY = cmds.getAttr(object + '.rotateY', lock=True)
        lockZ = cmds.getAttr(object + '.rotateZ', lock=True)

        lock_value_cache[object] = [lockX, lockY, lockZ]

        cmds.setAttr(object + '.rotateX', lock=False)
        cmds.setAttr(object + '.rotateY', lock=False)
        cmds.setAttr(object + '.rotateZ', lock=False)


def apply_lock_cache_back():
    for item in lock_value_cache:
        cmds.setAttr(item + '.rotateX', lock=lock_value_cache[lock_value_cache][0])
        cmds.setAttr(item + '.rotateX', lock=lock_value_cache[lock_value_cache][1])
        cmds.setAttr(item + '.rotateX', lock=lock_value_cache[lock_value_cache][2])


def apply_animation(type_of_node):
    if not target_root:
        cmds.confirmDialog(title='Error', message='Please select a root object for "target" first.', button='OK')
        return
    if not animated_root:
        cmds.confirmDialog(title='Error', message='Please select a root object for "animated" first.', button='OK')
        return
    cmds.currentTime(0, edit=True)

    animated_children = cmds.listRelatives(animated_root[0], allDescendents=True, type='transform', path=True)
    animated_children.append(animated_root[0])
    target_children = cmds.listRelatives(target_root[0], allDescendents=True, type=type_of_node, path=True)
    is_shapes = type_of_node == 'nurbsCurve'

    if is_shapes:
        target_children = [get_transform_of_shape(relative) for relative in target_children]

    target_children.append(target_root[0])

    cache_locks(target_children)
    reset_rotations(animated_children)
    create_parent_constraint(animated_children, target_children)

    clip_duration = cmds.keyframe(animated_children[-1], q=True)
    cmds.playbackOptions(edit=True, animationStartTime=0)
    cmds.playbackOptions(edit=True, animationEndTime=clip_duration[-1])
    min_time = cmds.playbackOptions(edit=True, minTime=0)
    max_time = cmds.playbackOptions(edit=True, maxTime=clip_duration[-1])

    cmds.bakeResults(target_children, t=(min_time, max_time), simulation=True)

    delete_parent_constraint()
    apply_lock_cache_back()


def reset_rotations(object_list):
    for obj in object_list:
        cmds.setAttr(obj + '.rotateX', 0)
        cmds.setAttr(obj + '.rotateY', 0)
        cmds.setAttr(obj + '.rotateZ', 0)
        cmds.setAttr(obj + '.rotate', 0, 0, 0)
        cmds.setKeyframe(obj, attribute='rotate')


def create_parent_constraint(animated_children, target_children):
    for animated_child in animated_children:
        animated_child_name = animated_child.split(':')[-1]
        for target_child in target_children:
            if animated_child_name in target_child:
                constraint = cmds.parentConstraint(animated_child, target_child, mo=True, st=['x', 'y', 'z'])
                created_parentConstraints.append(constraint)


def delete_parent_constraint():
    for constraint in created_parentConstraints:
        cmds.delete(constraint)
    created_parentConstraints.clear()


if cmds.window('animation_transfer_window', exists=True):
    cmds.deleteUI('animation_transfer_window')

window = cmds.window('animation_transfer_window', title='Animation Transfer', widthHeight=(400, 200))
cmds.columnLayout(adjustableColumn=True)

cmds.text(label='Select the root object for "Target to apply animation":')
target_text_field = cmds.textField('target_textField', editable=False)
target_button = cmds.button(label='Select Target Root', command=select_target_root)

cmds.text(label='Select the root object for "Animotive Export":')
animated_text_field = cmds.textField('animated_textField', editable=False)
animated_button = cmds.button(label='Select Animotive Export Root', command=select_animated_root)

apply_button = cmds.button(label='Apply Animation', command=lambda *_: apply_animation('joint'))
apply_button = cmds.button(label='Apply Animation to controls(nurbsCurve)',
                           command=lambda *_: apply_animation('nurbsCurve'))
cmds.showWindow(window)
