import maya.cmds as cmds
import json
import ntpath
import maya.mel

def select_target_root(*args):
    global target_root
    target_root = cmds.ls(selection=True, type='transform')

    if len(target_root) != 1:
        target_root = None
        cmds.textField('target_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message='Please select one root object for "target".', button='OK')
    else:
        cmds.textField('target_textField', edit=True, text=target_root[0])


def get_blendshape_node_from_geo():
    nodes = []
    obj_selection = target_root

    history = cmds.listHistory(obj_selection)
    for node in history:
        if cmds.nodeType(node) == 'blendShape':
            nodes.append(node)

    return (nodes)


def set_playback_speed():
    frameCount = len(facialAnimationFrames)
    cmds.currentUnit(time='ntscf')
    cmds.playbackOptions(edit=True, animationStartTime=0)
    cmds.playbackOptions(edit=True, animationEndTime=frameCount)
    cmds.playbackOptions(edit=True, minTime=0)
    cmds.playbackOptions(edit=True, maxTime=frameCount)


def set_keyframes_from_json(*args):
    print(target_root)
    if target_root is None:
        print("Nothing was selected !")
    character_geos = facialAnimationClipData['characterGeos']
    facialAnimation_frames = facialAnimationClipData['facialAnimationFrames']
    names = get_blendshape_node_from_geo()

    for frame in range(0, len(facialAnimation_frames)):
        blendshapes_per_frame = facialAnimation_frames[frame]

        for blendshapeUsed in blendshapes_per_frame["blendShapesUsed"]:
            geo_index = blendshapeUsed["g"]
            geo_name = character_geos[geo_index]["skinnedMeshRendererName"]
            blendshape_names = character_geos[geo_index]["blendShapeNames"]
            bs_index = blendshapeUsed["i"]
            bs_name = blendshape_names[bs_index]
            bs_value = blendshapeUsed["v"] / 100
            # blendshapeIndex = blendshapeUsed['i']

            for name in names:
                if geo_name in name:
                    targetBlendShape = name + "." + bs_name
                    cmds.setKeyframe(targetBlendShape, time=frame, value=bs_value)


filters = "JSON files (*.json)"

pathOfFileToLoad =cmds.fileDialog2(fileFilter=filters, dialogStyle=2, fileMode=1)


file = open(pathOfFileToLoad[0], 'r')
facialAnimationClipData = json.load(file)
characterGeos = facialAnimationClipData['characterGeos']
thislist = []
for characterGeosIndex in range(0, len(characterGeos)):
    geoName = characterGeos[characterGeosIndex]['skinnedMeshRendererName']
    thislist.append(geoName)

deltaFrameTime = facialAnimationClipData['fixedDeltaTimeBetweenKeyFrames']
facialAnimationFrames = facialAnimationClipData['facialAnimationFrames']
clipDuration = (len(facialAnimationFrames))

set_playback_speed()


if cmds.window('animation_transfer_window', exists=True):
    cmds.deleteUI('animation_transfer_window')

window = cmds.window('animation_transfer_window', title='Face Animation Transfer', widthHeight=(400, 200))
cmds.columnLayout(adjustableColumn=True)

cmds.text(label='Select target object to apply blendshape animation:')
target_text_field = cmds.textField('target_textField', editable=False)
target_button = cmds.button(label='Select', command=select_target_root)

apply_button = cmds.button(label='Apply Animation', command=set_keyframes_from_json)

cmds.showWindow(window)