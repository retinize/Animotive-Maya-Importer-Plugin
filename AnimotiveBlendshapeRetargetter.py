import maya.cmds as cmds
import json
import ntpath
import maya.mel


target_root = None
pathOfFileToLoad=None

def git_hub_readme(*args):
    url = "https://github.com/retinize/Animotive-Maya-Importer-Plugin/blob/main/README.md"
    webbrowser.open(url)

def select_target_root(*args):
    global target_root
    target_root = cmds.ls(selection=True, type='transform')

    if len(target_root) != 1:
        target_root = None
        cmds.textField('target_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message='Please select one root object for "target".', button='OK')
    else:
        cmds.textField('target_textField', edit=True, text=target_root[0])

def open_file_browser(*args):
    global pathOfFileToLoad
    filters = "JSON files (*.json)"

    pathOfFileToLoad =cmds.fileDialog2(fileFilter=filters, dialogStyle=2, fileMode=1)

    if len(pathOfFileToLoad) != 1:
        pathOfFileToLoad = None
        cmds.textField('json_file_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message='Please select one root object for "target".', button='OK')
    else:
        cmds.textField('json_file_textField', edit=True, text=pathOfFileToLoad[0])

def get_blendshape_node_from_geo():
    nodes = []
    obj_selection = target_root

    history = cmds.listHistory(obj_selection)

    for node in history:
        if cmds.nodeType(node) == 'blendShape':
            nodes.append(node)
    return (nodes)


def set_playback_speed(facial_animation_frames):

    frame_count = len(facial_animation_frames)
    cmds.currentUnit(time='ntscf')
    cmds.playbackOptions(edit=True, animationStartTime=0)
    cmds.playbackOptions(edit=True, animationEndTime=frame_count)
    cmds.playbackOptions(edit=True, minTime=0)
    cmds.playbackOptions(edit=True, maxTime=frame_count)


def set_keyframes_from_json(*args):
   
    if target_root is None:
        print("Target object was not selected !")
        return

    if pathOfFileToLoad is None:
        print("No json file was selected..")
        return

    cmds.currentTime(0, edit=True)
    file = open(pathOfFileToLoad[0], 'r')

    facial_animation_clip_data = json.load(file)

    facial_animation_frames = facial_animation_clip_data['facialAnimationFrames']
    set_playback_speed(facial_animation_frames)

    character_geos = facial_animation_clip_data['characterGeos']
    names = get_blendshape_node_from_geo()

    if not names:
        cmds.confirmDialog(title='Message',
                           message="Selected target doesn't have any shape ... ",
                           button='OK')
        return

    is_failed = False
    fail_count = 0

    for frame in range(0, len(facial_animation_frames)):
        blendshapes_per_frame = facial_animation_frames[frame]

        if fail_count==len(names):
            cmds.confirmDialog(title='Warning', message="No matched shape found in selected object, please select another object and try again ", button='OK')
            is_failed=True
            break

        for blendshapeUsed in blendshapes_per_frame["blendShapesUsed"]:
            geo_index = blendshapeUsed["g"]
            #geo_name = character_geos[geo_index]["skinnedMeshRendererName"]
            blendshape_names = character_geos[geo_index]["blendShapeNames"]
            bs_index = blendshapeUsed["i"]
            bs_name = blendshape_names[bs_index]
            bs_value = blendshapeUsed["v"] / 100
            # blendshapeIndex = blendshapeUsed['i']

            for name in names:
                targetBlendShape = name + "." + bs_name

                try:
                    cmds.setKeyframe(targetBlendShape, time=frame, value=bs_value)
                except:
                    fail_count+=1
                    continue
                    # print("There's no node with the name '"+targetBlendShape+"' please select another object and try again ")


    if not is_failed :
        cmds.confirmDialog(title='Message', message="Success ! ", button='OK')

if cmds.window('animation_transfer_window', exists=True):
    cmds.deleteUI('animation_transfer_window')

window = cmds.window('animation_transfer_window', title='Face Animation Transfer', resizeToFitChildren = True)
cmds.columnLayout(adjustableColumn=True)


cmds.text(label='Select JSON file that contains the blendshape animation:')
json_file_text_field = cmds.textField('json_file_textField', editable=False)
open_file_browser = cmds.button(label='Select', command=open_file_browser)

cmds.text(label='Select target object to apply blendshape animation:')
target_text_field = cmds.textField('target_textField', editable=False)
target_button = cmds.button(label='Select', command=select_target_root)


cmds.text(label='')
apply_button = cmds.button(label='Apply Animation', command=set_keyframes_from_json)

cmds.text(label="--------------------------------------------------------------------------------------------------------------------------------------------------------------------", enable=False)

cmds.button(label='Help', command=git_hub_readme)

cmds.showWindow(window)
