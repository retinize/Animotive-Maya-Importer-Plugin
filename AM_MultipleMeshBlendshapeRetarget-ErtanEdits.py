import maya.cmds as cmds
import json
import ntpath
import maya.mel

def select_target_root(*args):
    print("select")
    global target_root
    target_root = cmds.ls(selection=True, type='transform')

    if len(target_root) != 1:
        target_root = None
        cmds.textField('target_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message='Please select one root object for "target".', button='OK')
    else:
        cmds.textField('target_textField', edit=True, text=target_root[0])

def GetBlendshapeNodefromGeo():
    nodes = []
    objSelection = target_root
    
    history = cmds.listHistory(objSelection)
    for node in history:
        if cmds.nodeType(node) == 'blendShape':
            nodes.append(node)
        
    return (nodes)
          
def SetPlayBackSpeed():
    clipDuration = (len(facialAnimationFrames)-1)*deltaFrameTime
    fps = -1*deltaFrameTime
    frameCount = len(facialAnimationFrames)
    cmds.currentUnit(time = 'ntscf')
    cmds.playbackOptions(edit = True, animationStartTime = 0)
    cmds.playbackOptions(edit = True, animationEndTime = frameCount)
    cmds.playbackOptions(edit = True, minTime = 0)
    cmds.playbackOptions(edit = True, maxTime = frameCount)
    


def SetKeyFramesFromJSON(*args):
    print(target_root)
    if target_root == None:
        print("Nothing was selected !")
    characterGeos = facialAnimationClipData['characterGeos']
    facialAnimationFrames = facialAnimationClipData['facialAnimationFrames'] 
    names = GetBlendshapeNodefromGeo()

    for frame in range (0, len(facialAnimationFrames)):
        blendshapesPerFrame=facialAnimationFrames[frame]
        
        for blendshapeUsed in blendshapesPerFrame["blendShapesUsed"]:
            geoIndex = blendshapeUsed["g"]
            geoName = characterGeos[geoIndex]["skinnedMeshRendererName"]
            blendshapeNames = characterGeos[geoIndex]["blendShapeNames"]
            bsIndex = blendshapeUsed["i"]
            bsName = blendshapeNames[bsIndex]
            bsValue = blendshapeUsed["v"]/100
            blendshapeIndex = blendshapeUsed['i']
            
            for name in names:
                if geoName in name:
                    targetBlendShape = name + "." + bsName
                    cmds.setKeyframe(targetBlendShape, time=frame, value=bsValue) 
                    
SetPlayBackSpeed()                   
if cmds.window('animation_transfer_window', exists=True):
    cmds.deleteUI('animation_transfer_window')

window = cmds.window('animation_transfer_window', title='Face Animation Transfer', widthHeight=(400, 200))
cmds.columnLayout(adjustableColumn=True)


cmds.text(label='Select the root object for "target":')
target_text_field = cmds.textField('target_textField', editable=False)
target_button = cmds.button(label='Select', command=select_target_root)


apply_button = cmds.button(label='Apply Animation', command=SetKeyFramesFromJSON)

cmds.showWindow(window)


#Here please puts the path of the file that you want to load, I leave one as an example:
pathOfFileToLoad = r'C:\Users\jack\Desktop\FBX TESTING\multiple blendshapes macbeth\Testttt_Scene 1_Group1_Take1_ClipNum1_Macbeth_FaceAnim_T_00_00_00.json'
file = open(pathOfFileToLoad, 'r')
facialAnimationClipData = json.load(file)
characterGeos = facialAnimationClipData['characterGeos']
thislist = []
for characterGeosIndex in range(0, len(characterGeos)):
        geoName = characterGeos[characterGeosIndex]['skinnedMeshRendererName']
        thislist.append(geoName)
        

deltaFrameTime = facialAnimationClipData['fixedDeltaTimeBetweenKeyFrames']
facialAnimationFrames = facialAnimationClipData['facialAnimationFrames']
#clipDuration = (len(facialAnimationFrames)-1)*deltaFrameTime
clipDuration = (len(facialAnimationFrames))


