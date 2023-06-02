import maya.cmds as cmds
import re
import math

created_parentConstraints =[]
tPoseRotations = {}

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

def apply_animation(*args):
    if not target_root:
        cmds.confirmDialog(title='Error', message='Please select a root object for "target" first.', button='OK')
        return
    if not animated_root:
        cmds.confirmDialog(title='Error', message='Please select a root object for "animated" first.', button='OK')
        return
    cmds.currentTime(0, edit=True)
    
    animated_children = cmds.listRelatives(animated_root[0], allDescendents=True, type='transform',path=True)
    animated_children.append(animated_root[0])
    target_children = cmds.listRelatives(target_root[0], allDescendents=True, type='joint',path=True) 
    target_children.append(target_root[0])
    totalCount=len(animated_children)
    current=0
    targetRootName=animated_root[0].split(':')[-1]
    
    reset_rotations(animated_children)
    create_parent_constraint(animated_children,target_children)
    
    clipduration = cmds.keyframe(animated_children[-1], q = True)
    cmds.playbackOptions(edit = True, animationStartTime = 0)
    cmds.playbackOptions(edit = True, animationEndTime = clipduration[-1])
    minTIME = cmds.playbackOptions(edit = True, minTime = 0)
    maxTIME = cmds.playbackOptions(edit = True, maxTime = clipduration[-1])

    cmds.bakeResults(target_children, t=(minTIME,maxTIME), simulation = True)  
    
    delete_parent_constraint()

                         
def reset_rotations(object_list):
    for obj in object_list:
        cmds.setAttr(obj + '.rotateX', 0)
        cmds.setAttr(obj + '.rotateY', 0)
        cmds.setAttr(obj + '.rotateZ', 0)
        cmds.setAttr(obj + '.rotate', 0, 0, 0)
        cmds.setKeyframe(obj, attribute='rotate')
        
def create_parent_constraint(animated_children,target_children):
     for animated_child in animated_children:
        animated_child_name = animated_child.split(':')[-1]        
        for target_child in target_children:
            if animated_child_name in target_child:
                constraint=cmds.parentConstraint(animated_child,target_child, mo = True, st = ['x','y','z'])
                created_parentConstraints.append(constraint)
def delete_parent_constraint():
    for constraint in created_parentConstraints:
        cmds.delete(constraint)
    created_parentConstraints.clear()   
        

if cmds.window('animation_transfer_window', exists=True):
    cmds.deleteUI('animation_transfer_window')

window = cmds.window('animation_transfer_window', title='Animation Transfer', widthHeight=(400, 200))
cmds.columnLayout(adjustableColumn=True)

cmds.text(label='Select the root object for "target":')
target_text_field = cmds.textField('target_textField', editable=False)
target_button = cmds.button(label='Select', command=select_target_root)

cmds.text(label='Select the root object for "animated":')
animated_text_field = cmds.textField('animated_textField', editable=False)
animated_button = cmds.button(label='Select', command=select_animated_root)

apply_button = cmds.button(label='Apply Animation', command=apply_animation)

cmds.showWindow(window)