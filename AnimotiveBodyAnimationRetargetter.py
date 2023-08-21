import maya.cmds as cmds
import re
import math
import webbrowser

target_root = None
user_selected_root_bone=None
animated_root= None

created_parentConstraints = []
tPoseRotations = {}


def select_target_root(*args):
    global target_root
    target_root = cmds.ls(selection=True, type='transform')

    if len(target_root) != 1:
        target_root = None
        cmds.textField('target_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message='Please select one root joint for "target".', button='OK')
    else:
        cmds.textField('target_textField', edit=True, text=target_root[0])


def select_root_bone(*args):
    global user_selected_root_bone
    user_selected_root_bone = cmds.ls(selection=True, type='transform')

    if len(user_selected_root_bone) != 1:
        user_selected_root_bone = None
        cmds.textField('user_selected_root_bone_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message="Please select the pelvis joint (Root/Hips)", button='OK')
    else:
        cmds.textField('user_selected_root_bone_textField', edit=True, text=user_selected_root_bone[0])


def select_animated_root(*args):
    global animated_root
    animated_root = cmds.ls(selection=True, type='transform')

    if len(animated_root) != 1:
        animated_root = None
        cmds.textField('animated_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message='Please select one root object for "Animotive Export".', button='OK')
    else:
        cmds.textField('animated_textField', edit=True, text=animated_root[0])


def apply_animation(*args):
    if not target_root:
        cmds.confirmDialog(title='Error', message='Please select a root of the target where you want the animation to be applied.', button='OK')
        return
    if not animated_root:
        cmds.confirmDialog(title='Error', message='Please select a root object of the animotive export', button='OK')
        return
    if not user_selected_root_bone:
        cmds.confirmDialog(title='Error', message='Please select a root bone joint of the target', button='OK')
        return

    cmds.currentTime(0, edit=True)

    animated_children = cmds.listRelatives(animated_root[0], allDescendents=True, type='transform', path=True)
    animated_children.append(animated_root[0])
    target_children = cmds.listRelatives(target_root[0], allDescendents=True, type='joint', path=True)
    target_children.append(target_root[0])

    #reset_rotations(animated_children)
    create_parent_constraint(animated_children, target_children)
    clip_duration=0
    
    for child in animated_children:
        key_times = cmds.keyframe(child, q=True)
        if key_times is not None and is_list_zero(key_times)==False:
            print("HERE "+str(key_times) )
            clip_duration = key_times
            break

        
    cmds.playbackOptions(edit=True, animationStartTime=0)
    cmds.playbackOptions(edit=True, animationEndTime=clip_duration[-1])
    min_time = cmds.playbackOptions(edit=True, minTime=0)
    max_time = cmds.playbackOptions(edit=True, maxTime=clip_duration[-1])
    

    cmds.bakeResults(target_children, t=(min_time, max_time), simulation=True)

    delete_parent_constraint()


#def reset_rotations(object_list):
    #for obj in object_list:
        #cmds.setAttr(obj + '.rotateX', 0)
        #cmds.setAttr(obj + '.rotateY', 0)
        #cmds.setAttr(obj + '.rotateZ', 0)
        #cmds.setAttr(obj + '.rotate', 0, 0, 0)
        #cmds.setKeyframe(obj, attribute='rotate')
        
def is_list_zero(target_list):
    for item in target_list:
        if item != 0.0:
            return False
    
    return True;        
            
            

def create_parent_constraint(animated_children, target_children):
    for animated_child in animated_children:
        animated_child_name = animated_child.split(':')[-1]
        for target_child in target_children:
            if animated_child_name in target_child:
                is_root = target_child == user_selected_root_bone[0]
                constraint = None
                if is_root:
                    constraint = cmds.parentConstraint(animated_child, target_child, mo=True)
                else:
                    constraint = constraint = cmds.parentConstraint(animated_child, target_child, mo=True, st=['x', 'y', 'z'])
                created_parentConstraints.append(constraint)


def delete_parent_constraint():
    for constraint in created_parentConstraints:
        cmds.delete(constraint)
    del created_parentConstraints[:]


def git_hub_readme(*args):
    url = "https://github.com/retinize/Animotive-Maya-Importer-Plugin/blob/main/README.md"
    webbrowser.open(url)


if cmds.window('animation_transfer_window', exists=True):
    cmds.deleteUI('animation_transfer_window')

window = cmds.window('animation_transfer_window', title='Animotive Animation Transfer', resizeToFitChildren = True)
cmds.window(window,edit=True,sizeable=True)
cmds.columnLayout(adjustableColumn=True)

cmds.text(label='')
cmds.text(label='Select the targets bind joint group:')
target_text_field = cmds.textField('target_textField', editable=False)
target_button = cmds.button(label='Select target joint group', command=select_target_root)


cmds.text(label='')
cmds.text(label='Select the targets root joint:')
user_selected_root_bone_text_field = cmds.textField('user_selected_root_bone_textField', editable=False)
user_selected_root_bone_button = cmds.button(label='Select Target Root Joint', command=select_root_bone)


cmds.text(label='')
cmds.text(label='Select the root object for "Animotive Export":')
animated_text_field = cmds.textField('animated_textField', editable=False)
animated_button = cmds.button(label='Select Animotive Export Root', command=select_animated_root)


cmds.text(label="--------------------------------------------------------------------------------------------------------------------------------------------------------------------", enable=False)
apply_button = cmds.button(label='Apply Animation', command=apply_animation)

cmds.text(label="--------------------------------------------------------------------------------------------------------------------------------------------------------------------", enable=False)

cmds.button(label='Help', command= 'git_hub_readme()')

cmds.showWindow(window)
