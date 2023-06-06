import maya.cmds as cmds
import json
import ntpath
import maya.mel
import sys

def OpenAndReadJSONFileDialogWindow():
    
    pathOfFileToLoad = cmds.fileDialog2(fileFilter="JSON Files (*.json)", dialogStyle=2, fileMode=1, caption="Select JSON File")
    
    if pathOfFileToLoad:
        
        try:
            with open(pathOfFileToLoad[0], 'r') as animotiveJSONFile:
                facialAnimationClipData = json.load(animotiveJSONFile)
                print(facialAnimationClipData)
                sys.stdout.write("JSON Read.")   
        except AnimotiveJSONFileNotFoundError:
            print(f"File Could not be found: {file_path[0]}")
        except json.JSONDecodeError as j:
            sys.stdout.write(f"Error reading JSON data found in file: {j}")
    else:
        sys.stdout.write("No file was selected, please select a file.")
    


def GetAndStoreBlendshpeNodeFromGeo():
    selection = cmds.ls(sl=True)
    bshpNodes = []
    for obj in selection:
        for bshpNode in cmds.listHistory(obj):
            if cmds.nodeType(bshpNode) == 'blendShape':
                bshpNodes.append(bshpNode)
    return bshpNodes

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
        print('geoIndex',geoIndex,':', characterGeos[geoIndex]['skinnedMeshRendererName'])
        blendShapesNames = characterGeos[geoIndex]['blendShapeNames']
        print('blendShapes found in this geo', len(blendShapesNames),':')
        for blendShapeIndex in range(0, len(blendShapesNames)):
            print('blendShapeIndex',blendShapeIndex,',', blendShapesNames[blendShapeIndex])
            
#def SetPlayBackSpeed():
    #clipDuration = (len(facialAnimationFrames)-1)*deltaFrameTime
    #fps = -1*deltaFrameTime
    #frameCount = len(facialAnimationFrames)
    #cmds.currentUnit(time = 'ntscf')
    #cmds.playbackOptions(edit = True, animationStartTime = 0)
    #cmds.playbackOptions(edit = True, animationEndTime = frameCount)
    #cmds.playbackOptions(edit = True, minTime = 0)
    #cmds.playbackOptions(edit = True, maxTime = frameCount)
    
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
                
    ##-- Update TimeSlider witht he start and end time of the animotive take
    
    clipDuration = (len(facialAnimationFrames)-1)*deltaFrameTime
    fps = -1*deltaFrameTime
    frameCount = len(facialAnimationFrames)
    cmds.currentUnit(time = 'ntscf')
    cmds.playbackOptions(edit = True, animationStartTime = 0)
    cmds.playbackOptions(edit = True, animationEndTime = frameCount)
    cmds.playbackOptions(edit = True, minTime = 0)
    cmds.playbackOptions(edit = True, maxTime = frameCount)


#Here please puts the path of the file that you want to load, I leave one as an example:
#pathOfFileToLoad = r'C:\Users\jack\Documents\MultipleSkinnedMeshRender\Testttt_Scene 1_Group1_Take1_ClipNum1_Macbeth_FaceAnim_T_00_00_00.json'
#file = open(pathOfFileToLoad, 'r')
#facialAnimationClipData = json.load(file)
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


def FacialAnimationRetargeterPlugin():
    if cmds.window('FacialAnimationRetargeterPlugin', exists = True):
        cmds.deleteUI ('FacialAnimationRetargeterPlugin')
    cmds.window ('FacialAnimationRetargeterPlugin', title = 'Facial Animation Retargeter UI', widthHeight = (300, 89), sizeable = False)
    cmds.columnLayout(adj = True)
    
    cmds.separator()
    cmds.text( label='Locate and Open JSON File' )
    cmds.button( label='Import JSON', command = 'OpenAndReadJSONFileDialogWindow()' )
    
    cmds.separator()
    cmds.text( label='Import Animotive Facial Capture' )
    cmds.button( label='Retarget Animation', command = 'SetKeyFramesFromJSON()()' )    
    
    cmds.showWindow('FacialAnimationRetargeterPlugin')
    
       
FacialAnimationRetargeterPlugin()