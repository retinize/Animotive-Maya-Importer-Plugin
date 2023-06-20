import maya.cmds as cmds
import json
import ntpath
import maya.mel


target_root = None
pathOfFileToLoad=None

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


def set_playback_speed(facial_animation_clip_data):

    facial_animation_frames = facial_animation_clip_data['facialAnimationFrames']
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

    content = cmds.textField(blendshape_text_field, query=True, text=True)
    if content is None:
        print("You need to type a blendshape name..")
        return

    if pathOfFileToLoad is None:
        print("No json file was selected..")
        return


    file = open(pathOfFileToLoad[0], 'r')

    facial_animation_clip_data = json.load(file)

    set_playback_speed(facial_animation_clip_data)

    character_geos = facial_animation_clip_data['characterGeos']
    facial_animation_frames = facial_animation_clip_data['facialAnimationFrames']
    names = get_blendshape_node_from_geo()


    for frame in range(0, len(facial_animation_frames)):
        blendshapes_per_frame = facial_animation_frames[frame]

        for blendshapeUsed in blendshapes_per_frame["blendShapesUsed"]:
            geo_index = blendshapeUsed["g"]
            #geo_name = character_geos[geo_index]["skinnedMeshRendererName"]
            blendshape_names = character_geos[geo_index]["blendShapeNames"]
            bs_index = blendshapeUsed["i"]
            bs_name = blendshape_names[bs_index]
            bs_value = blendshapeUsed["v"] / 100
            # blendshapeIndex = blendshapeUsed['i']

            for name in names:
                if content in name:
                    targetBlendShape = name + "." + bs_name
                    cmds.setKeyframe(targetBlendShape, time=frame, value=bs_value)


if cmds.window('animation_transfer_window', exists=True):
    cmds.deleteUI('animation_transfer_window')

window = cmds.window('animation_transfer_window', title='Face Animation Transfer', widthHeight=(400, 200))
cmds.columnLayout(adjustableColumn=True)


cmds.text(label='Select JSON file that contains the blendshape animation:')
json_file_text_field = cmds.textField('json_file_textField', editable=False)
open_file_browser = cmds.button(label='Select', command=open_file_browser)

cmds.text(label='Select target object to apply blendshape animation:')
target_text_field = cmds.textField('target_textField', editable=False)
target_button = cmds.button(label='Select', command=select_target_root)

cmds.text(label='Write the shape name that you want to apply animation to :')
blendshape_text_field = cmds.textField(placeholderText='Enter your text here')

apply_button = cmds.button(label='Apply Animation', command=set_keyframes_from_json)

cmds.showWindow(window)