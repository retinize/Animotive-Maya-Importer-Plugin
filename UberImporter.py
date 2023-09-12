import maya.cmds as cmds
import sys
import re

def get_last_composition_index():
    elements = cmds.ls()
    filtered_elements = [elem for elem in elements if re.search("MyComposition\d+", elem)]
    
    indices = [int(re.search("\d+", elem).group()) for elem in filtered_elements]
    if not indices:
        return "1"
    
    return str(max(indices) + 1)

def has_keyframes(node_name):
    for attr in cmds.listAttr(node_name, keyable=True) or []:
        if cmds.keyframe(node_name + '.' + attr, query=True, keyframeCount=True) > 0:
            return True
    return False



selection = cmds.ls(selection=True)

if selection is None or len(selection)==0:
    print("Nothing was selected")
    sys.exit()

all_children = cmds.listRelatives(selection, allDescendents=True, type='joint', path=True)

if len(all_children)==0:
    sys.exit()

try:
    cmds.workspaceControl('Control')
    cmds.timeEditorPanel()
except RuntimeError as e:
    if "Object's name" not in str(e):
        print("Error:", e)
    else:
        print("Time Editor already exists")
clipIndex = 0

last_composition_name = 'MyComposition'+get_last_composition_index()
cmds.timeEditorComposition(last_composition_name)

temp = ";".join(all_children)

cmds.timeEditorAnimSource("anim_Clip1",ao= temp, addRelatedKG=True, removeSceneAnimation=True, includeRoot=True, recursively=True)







