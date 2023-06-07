import maya.cmds as cmds
import json
import ntpath
import maya.mel


def GetBlendshapeNodefromGeo():
    selection = cmds.ls(sl=True)
    nodes = []
    for obj in selection:
        for node in cmds.listHistory(obj):
            if cmds.nodeType(node) == 'blendShape':
                nodes.append(node)
    return nodes

def PrintBlendShapeDataFromFrame(frameNumber):
    print('Blendshape data for frame',frameNumber,':')
    blendShapesUsed = facialAnimationFrames[frameNumber]['blendShapesUsed']
    for blendShapeDataIndex in range(0, len(blendShapesUsed)):
        specificBlendShape = blendShapesUsed[blendShapeDataIndex]
        skinnedMeshRendererIndex = specificBlendShape['g']
        blendShapeIndex = specificBlendShape['i']
        value = specificBlendShape['v']
        print((skinnedMeshRendererIndex, blendShapeIndex, value))

def PrintCharacterGeosUsed():
    characterGeos = facialAnimationClipData['characterGeos']
    for geoIndex in range (0,len(characterGeos)):
        print('geoIndex',geoIndex,':', characterGeos[geoIndex]['name'])
        blendShapesNames = characterGeos[geoIndex]['blendShapeNames']
        print('blendShapes found in this geo', len(blendShapesNames),':')
        for blendShapeIndex in range(0, len(blendShapesNames)):
            print('blendShapeIndex',blendShapeIndex,',', blendShapesNames[blendShapeIndex])
            
def SetPlayBackSpeed():
    clipDuration = (len(facialAnimationFrames)-1)*deltaFrameTime
    fps = -1*deltaFrameTime
    frameCount = len(facialAnimationFrames)
    cmds.currentUnit(time = 'ntscf')
    cmds.playbackOptions(edit = True, animationStartTime = 0)
    cmds.playbackOptions(edit = True, animationEndTime = frameCount)
    cmds.playbackOptions(edit = True, minTime = 0)
    cmds.playbackOptions(edit = True, maxTime = frameCount)
    


def SetKeyFramesFromJSON():
    #facialAnimationClipData
    characterGeos = facialAnimationClipData['characterGeos']
    facialAnimationFrames = facialAnimationClipData['facialAnimationFrames'] 
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
            cmds.select(geoName)
            names = GetBlendshapeNodefromGeo()
            if len(names) > 0:
                targetBlendShape = names[0] + "." + bsName
                cmds.setKeyframe(targetBlendShape, time=frame, value=bsValue) 



#Here please puts the path of the file that you want to load, I leave one as an example:
pathOfFileToLoad = r'C:\Users\jack\Desktop\FBX TESTING\multiple blendshapes macbeth\Testttt_Scene 1_Group1_Take1_ClipNum1_Macbeth_FaceAnim_T_00_00_00.json'
file = open(pathOfFileToLoad, 'r')
facialAnimationClipData = json.load(file)
characterGeos = facialAnimationClipData['characterGeos']
thislist = []
for characterGeosIndex in range(0, len(characterGeos)):
        geoName = characterGeos[characterGeosIndex]['skinnedMeshRendererName']
        thislist.append(geoName)
        cmds.select(geoName) 
        

deltaFrameTime = facialAnimationClipData['fixedDeltaTimeBetweenKeyFrames']
facialAnimationFrames = facialAnimationClipData['facialAnimationFrames']
#clipDuration = (len(facialAnimationFrames)-1)*deltaFrameTime
clipDuration = (len(facialAnimationFrames))

SetPlayBackSpeed()
SetKeyFramesFromJSON()