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

all_children = cmds.listRelatives(selection, allDescendents=True, type='transform', path=True)

if len(all_children)==0:
    sys.exit()

try:
    cmds.workspaceControl('Control')
    cmds.timeEditorPanel()
except:
    print("it already exists")
     
clipIndex = 0

last_composition_name = 'MyComposition'+get_last_composition_index()
cmds.timeEditorComposition(last_composition_name)
#cmds.timeEditorTracks(trackName="Track1", path='MyComposition', addTrack=1)
for child in all_children:
    if has_keyframes(child):

        cmds.timeEditorClip(child, track=last_composition_name+":1",clipId=clipIndex)
        #cmds.timeEditorClip(child, track="MyComposition|Track1",animSource=True,clipId=clipIndex)
        clipIndex+=1




#time_editor_objects = cmds.ls(type="timeEditor")
#if time_editor_objects:
#    time_editor_panel = time_editor_objects[0]


