import asyncio
import maya.cmds as cmds
import sys
import re
import os
import xml.etree.ElementTree as ET
import json
import time

fbx_files = None
import_directory = None
root_group_selection = None
facial_animation_target_selection =None
root_bone_selection = None
created_parent_constraints = []
last_composition_name = ""
blendshape_node = None
xml_data_list = []

class XmlData:

    file_name = ""
    in_frame = -1
    out_frame = -1
    start_frame = -1
    end_frame = -1

    def __init__(self):
        self.file_name = ""
        self.in_frame = -1
        self.out_frame = -1
        self.start_frame = -1
        self.end_frame = -1

    def set_data(self,fileName,inFrame,outFrame,startFrame,endFrame):
        self.file_name = fileName
        self.in_frame = inFrame
        self.out_frame=outFrame

        self.start_frame = startFrame
        self.end_frame=endFrame


# ---- Beginning of Body Retargeting ----


def delete_parent_constraints_recursive(obj):
    descendents = cmds.listRelatives(obj, allDescendents=True, fullPath=True,type='parentConstraint') or []
    if descendents:
        cmds.delete(descendents)

async def apply_body_animation(animated_root,target_root):
    print("Applying body animation")
    if not target_root:
        cmds.confirmDialog(title='Error', message='Please select a root of the target where you want the animation to be applied.', button='OK')
        return
    if not animated_root:
        cmds.confirmDialog(title='Error', message='Please select a root object of the animotive export', button='OK')
        return
    if not root_group_selection:
        cmds.confirmDialog(title='Error', message='Please select a root bone joint of the target', button='OK')
        return

    result=None

    try:
        delete_parent_constraints_recursive(target_root)
        cmds.currentTime(0, edit=True)

        animated_children = cmds.listRelatives(animated_root, allDescendents=True, type='transform', path=True)
        animated_children.append(animated_root)
        target_children = cmds.listRelatives(target_root, allDescendents=True, type='joint', path=True)
        target_children.append(target_root)

        # reset_rotations(animated_children)
        create_parent_constraint(animated_children, target_children)
        frame_count = 0

        for child in animated_children:
            key_times = cmds.keyframe(child, q=True)
            if key_times is not None and is_list_zero(key_times) == False:
                first_frame = min(key_times)
                last_frame = max(key_times)

                frame_count = int(last_frame - first_frame + 1)
                break
        cmds.playbackOptions(edit=True, animationStartTime=0,framesPerSecond=60)
        cmds.playbackOptions(edit=True, animationEndTime=frame_count,framesPerSecond=60)
        cmds.playbackOptions(edit=True, minTime=0,framesPerSecond=60)
        cmds.playbackOptions(edit=True, maxTime=frame_count,framesPerSecond=60)

        cmds.bakeResults(target_children, t=(first_frame, last_frame), simulation=True,sampleBy=1)
        delete_parent_constraint()
        result = True #Successfull operation
    except RuntimeError as e:
        print("An exception was thrown : ",e)#Failed op
        result = False

    return result


def reset_rotations(object_list):
    for obj in object_list:
        cmds.setAttr(obj + '.rotateX', 0)
        cmds.setAttr(obj + '.rotateY', 0)
        cmds.setAttr(obj + '.rotateZ', 0)
        cmds.setAttr(obj + '.rotate', 0, 0, 0)
        cmds.setKeyframe(obj, attribute='rotate')

def is_list_zero(target_list):
    return(all(x == 0.0 for x in target_list))  

def is_parent(possible_parent, child):
    parent_of_child = cmds.listRelatives(child, parent=True)

    if not parent_of_child:
        return False

    return parent_of_child[0] == possible_parent

def create_parent_constraint(animated_children, target_children):
    for animated_child in animated_children:
        animated_child_name = animated_child.split(':')[-1]
        for target_child in target_children:
            if animated_child_name in target_child:
                is_root = target_child == root_bone_selection[0]
                is_hips = is_parent(root_bone_selection[0],target_child)
                constraint = None
                
                if is_root or is_hips:
                    constraint = cmds.parentConstraint(animated_child, target_child)
                else:
                    constraint = cmds.parentConstraint(animated_child, target_child,st=['x', 'y', 'z'])
                created_parent_constraints.append(constraint)


def delete_parent_constraint():
    for constraint in created_parent_constraints:
        if cmds.objExists(constraint[0]):
            cmds.delete(constraint[0])
    del created_parent_constraints[:]


# ---- End of Body Retargeting ----

def mute_all_tracks_in_composition(composition_name):
    if not cmds.objExists(composition_name):
        print(f"Composition {composition_name} does not exist!")
        return

    tracks = cmds.timeEditorTracks(composition_name, q=True, allTracks=True)

    if not tracks:
        print(f"No tracks found in {composition_name}")
        return

    for t in tracks:
        index = t.split(":")[1]
        cmds.timeEditorTracks(path=composition_name,trackIndex=int(index), edit=True, trackMuted=True)


# ---- Beginning of Facial Retargeting ----



def get_blendshape_weight_attributes(p_blendshape_node):
    weight_attrs = []

    num_weights = cmds.blendShape(p_blendshape_node, query=True, weightCount=True)

    for i in range(num_weights):
        weight_attr = "{}.weight[{}]".format(p_blendshape_node, i)
        weight_attrs.append(weight_attr)

    return weight_attrs


def get_graphics_root_group_and_set_text_field(*args):
    global facial_animation_target_selection
    facial_animation_target_selection = cmds.ls(selection=True, type='transform')

    if len(facial_animation_target_selection) != 1:
        facial_animation_target_selection = None
        cmds.textField('user_selected_graphics_group_text_field', edit=True, text='')
        cmds.confirmDialog(title='Error', message="Please select target object to apply facial animation", button='OK')
    else:
        cmds.textField('user_selected_graphics_group_text_field', edit=True, text=facial_animation_target_selection[0])

def set_playback_speed(facial_animation_clip_data):
    facial_animation_frames = facial_animation_clip_data['facialAnimationFrames']
    frame_count = len(facial_animation_frames)
    cmds.currentUnit(time='ntscf')
    cmds.playbackOptions(edit=True, animationStartTime=0,framesPerSecond=60)
    cmds.playbackOptions(edit=True, animationEndTime=frame_count,framesPerSecond=60)
    cmds.playbackOptions(edit=True, minTime=0,framesPerSecond=60)
    cmds.playbackOptions(edit=True, maxTime=frame_count,framesPerSecond=60)


def set_keyframes_from_json(path_of_file_to_load,name):

    if facial_animation_target_selection is None:
        print("Target object was not selected !")
        return

    if path_of_file_to_load is None:
        print("No json file was selected..")
        return

    cmds.currentTime(0, edit=True)
    json_file = open(path_of_file_to_load, 'r')

    facial_animation_clip_data = json.load(json_file)
    time_delta = facial_animation_clip_data["fixedDeltaTimeBetweenKeyFrames"]
    set_playback_speed(facial_animation_clip_data)

    character_geos = facial_animation_clip_data['characterGeos']
    facial_animation_frames = facial_animation_clip_data['facialAnimationFrames']
    is_failed=False

    all_geos_from_json=character_geos[0]["blendShapeNames"]

    for frame in range(0, len(facial_animation_frames)):
        blendshapes_per_frame = facial_animation_frames[frame]

        if is_failed:
            break
        for blendshapeUsed in blendshapes_per_frame["blendShapesUsed"]:
            geo_index = blendshapeUsed["g"]
            # geo_name = character_geos[geo_index]["skinnedMeshRendererName"]
            blendshape_names = character_geos[geo_index]["blendShapeNames"]
            bs_index = blendshapeUsed["i"]
            bs_name = blendshape_names[bs_index]
            bs_value = blendshapeUsed["v"] / 100
            # blendshapeIndex = blendshapeUsed['i']

            if is_failed:
                break

            targetBlendShape = name + "." + bs_name
            if not is_failed:
                try:
                    cmds.setKeyframe(targetBlendShape, time=frame, value=bs_value)
                except Exception as e:
                    #cmds.confirmDialog(title='Error', message="There's no node with the name '"+targetBlendShape+"' please select another object and try again ", button='OK')
                    print("Exception ! : ",e)
                    is_failed = True
                    break
            else:
                break

    #if not is_failed:    
    #    cmds.confirmDialog(title='Error', message=" Success ! ", button='OK')

    result = is_failed==False
    return result # if it's not failed than it was a successful operation

async def apply_given_json_file(full_json_path):
    print("Applying facial animation..")

    if blendshape_node is None:
        print("FAILED : Selected object doesn't have shape to write animation to ..")
        return False

    result= set_keyframes_from_json(full_json_path, blendshape_node)

    if not result:
        print("json import failed ! Make sure you have related json file for your animation exported from Animotive !")
    else:
        print("SUCCESS")


    return result

def get_blendshape_node(shapeNode):
    history = cmds.listHistory(shapeNode)
    blendshapes = cmds.ls(history, type='blendShape')
    return blendshapes[0] if blendshapes else None

async def delete_blendshape_keyframes(transform_node):
    shapes = cmds.listRelatives(transform_node, shapes=True)
    if not shapes:
        print("No shape node found for", transform_node)
        return

    blendshapeNode = get_blendshape_node(shapes[0])

    if not blendshapeNode:
        print("No blendshape node found for", transform_node)
        return


    numWeights = cmds.blendShape(blendshapeNode, query=True, weightCount=True)
    for i in range(numWeights):
        weightAttr = "{}.weight[{}]".format(blendshapeNode, i)
        if cmds.keyframe(weightAttr, query=True, keyframeCount=True) > 0:
            cmds.cutKey(weightAttr)

async def set_all_blendshapes_to_zero(transform_node):
    shapes = cmds.listRelatives(transform_node, shapes=True)
    if not shapes:
        print("No shape node found for", transform_node)
        return

    blendshapeNode = get_blendshape_node(shapes[0])

    if not blendshapeNode:
        print("No blendshape node found for", transform_node)
        return

    numWeights = cmds.blendShape(blendshapeNode, query=True, weightCount=True)
    for i in range(numWeights):
        weightAttr = "{}.weight[{}]".format(blendshapeNode, i)
        cmds.setAttr(weightAttr, 0)

# ---- End of Facial Retargeting ----

def load_fbx_plugin():
    plugin_name = "fbxmaya"
    if not cmds.pluginInfo(plugin_name, q=True, loaded=True):
        cmds.loadPlugin(plugin_name)

def choose_import_directory_and_retrieve_files(*args):
    global fbx_files
    global json_files
    global import_directory
    import_directory = browse_and_return_directory()

    if import_directory:
        fbx_files = collect_and_return_given_type_of_files_from_directory(import_directory,'.fbx')
        json_files = collect_and_return_given_type_of_files_from_directory(import_directory,'.json')

        cmds.textField('user_selected_import_directory_textField', edit=True,text=import_directory)
    


def browse_and_return_directory():
    directory = cmds.fileDialog2(dialogStyle=2, fileMode=3)
    if not directory:
        return []
    return directory[0]
  
def collect_and_return_given_type_of_files_from_directory(directory,file_extension_to_look_for):
    return [f for f in os.listdir(directory) if f.lower().endswith(file_extension_to_look_for)]
    

def get_selected_root_group_and_set_text_field(*args):
    global root_group_selection
    root_group_selection = cmds.ls(selection=True, type='transform')

    if len(root_group_selection) != 1:
        root_group_selection = None
        cmds.textField('user_selected_root_group_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message="Please select the parent object of the character rig group", button='OK')
    else:
        cmds.textField('user_selected_root_group_textField', edit=True, text=root_group_selection[0])

def get_selected_root_joint_and_set_text_field(*args):
    global root_bone_selection
    root_bone_selection = cmds.ls(selection=True, type='transform')

    if len(root_bone_selection) != 1:
        root_bone_selection = None
        cmds.textField('user_selected_root_joint_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message="Please select the character root Joint of the target character", button='OK')
    else:
        cmds.textField('user_selected_root_joint_textField', edit=True, text=root_bone_selection[0])

            

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


def create_time_editor_if_doesnt_exists():
    try:
        cmds.workspaceControl('Control')
        cmds.timeEditorPanel()
    except RuntimeError as e:
        if "Object's name" not in str(e):
            print("Error:", e)
        else:
            print("Time Editor already exists")


async def create_track_and_editor_clip(clip_name, target_root,facial_anim_result):
    cmds.currentTime(0, edit=True)

    all_children = cmds.listRelatives(target_root, allDescendents=True, type='joint', path=True) or []

    if not all_children:
        print("No object found to add time editor..")
        return
    joint_source_id=-1

    if all_children:
        all_children_jointed = ";".join(all_children)
        joint_source_id = cmds.timeEditorAnimSource(clip_name, ao=all_children_jointed,calculateTiming=True, addRelatedKG=True, removeSceneAnimation=True, includeRoot=True, recursively=True)

    facial_anim_source_id=-1
    if facial_anim_result:
        anim_source_name = clip_name+"_FacialAnimSource_"
        facial_anim_source_id = cmds.timeEditorAnimSource(anim_source_name,calculateTiming=True, ao=blendshape_node, addRelatedKG=True, removeSceneAnimation=True,includeRoot=True,recursively=True,type=["animCurveTL", "animCurveTA", "animCurveTT","animCurveTU"])

    return [joint_source_id,facial_anim_source_id,clip_name]


async def create_tracks_from_sources(tuple_array,connected_xml_datas):
    track_id=0

    for idx,tuple in enumerate(tuple_array):
        joint_source_id = tuple[0]
        facial_anim_source_id = tuple[1]
        clip_name = tuple[2]

        xml_value = None
        if clip_name in connected_xml_datas:
            xml_value = connected_xml_datas[clip_name]

        if joint_source_id!=-1:
            track_id+=1
            track_name = last_composition_name + "|track" + str(track_id)

            if xml_value:
                create_and_cut_clips_according_to_xml(xml_value,clip_name,track_name,joint_source_id,False)
            else:
                cmds.timeEditorClip(clip_name, track=track_name, animSource=anim_source_id, startTime=0)

        if facial_anim_source_id!=-1:
            track_id+=1
            facial_clip_name=clip_name + "_Facial"
            track_name = last_composition_name + "|track" + str(track_id)

            if xml_value:
                create_and_cut_clips_according_to_xml(xml_value,facial_clip_name,track_name,facial_anim_source_id,True)

            else:
                cmds.timeEditorClip(clip_name, track=track_name, animSource=facial_anim_source_id, rootClipId=-1,startTime=0)

def create_and_cut_clips_according_to_xml(xml_data_array,clip_name,track_name,source_id,is_facial):
    cmds.timeEditorTracks(path=last_composition_name, addTrack=-1, e=1)

    # xml_data = xml_data_array[0]
    for xml_data in xml_data_array:
        in_frame = int(xml_data.in_frame)
        out_frame = int(xml_data.out_frame)

        if is_facial:
            # face
            id = cmds.timeEditorClip(clip_name,track=track_name,animSource=source_id)
            cmds.timeEditorClip(clip_name,edit=True,clipId=id,trimStart=in_frame,trimEnd=out_frame,startTime=int(xml_data.start_frame))
        else:
            # body
            id = cmds.timeEditorClip(clip_name,track=track_name,animSource=source_id)
            cmds.timeEditorClip(clip_name,edit=True,clipId=id,trimStart=in_frame,trimEnd=out_frame,startTime=int(xml_data.start_frame))


def legalize_string(name):
    legal_name = ''.join(ch if ch.isalnum() else '_' for ch in name)
    return legal_name

def create_composition():
    global last_composition_name 
    last_composition_name = 'MyComposition'+get_last_composition_index()
    
    if not cmds.objExists(last_composition_name):
        cmds.timeEditorComposition(last_composition_name) 

async def remove_keyframes(root_object,should_remove_blendshapes):
    objects = cmds.listRelatives(root_object, allDescendents=True, fullPath=True)
    objects.append(root_object)

    if not should_remove_blendshapes:
        for current_object in objects:
            cmds.cutKey(current_object, clear=True)
    else:
        await delete_blendshape_keyframes(root_object)
      
async def import_single_fbx(full_path):
    cmds.FBXImport("-f",full_path,'-caller "FBXMayaTranslator" -importFormat "fbx"')

def import_xml(*args):
    global xml_data_list
    xml_file_full_path = browse_xml_file()
    if xml_file_full_path:

        cmds.textField('user_selected_xml_text_field', edit=True,text=xml_file_full_path)

        tree = ET.parse(xml_file_full_path)
        root = tree.getroot()
        xml_data_list = []

        clip_item = root.findall(".//clipitem")

        for clip_item in clip_item:
            file_name = clip_item.find("name").text
            if file_name is not None:
                file_full_path = file_name
                file_name_without_extension = os.path.splitext(file_full_path)[0]
                start_frame = clip_item.find("start").text
                end_frame = clip_item.find("end").text
                in_frame = clip_item.find("in").text
                out_frame = clip_item.find("out").text

                xml_data = XmlData()
                xml_data.__init__()
                xml_data.set_data(file_name_without_extension,in_frame,out_frame,start_frame,end_frame)
                xml_data_list.append(xml_data)


def browse_xml_file():
    file_filter = "XML Files (*.xml)"
    selected_file = cmds.fileDialog2(fileMode=1, fileFilter=file_filter)

    if selected_file:
        return selected_file[0]
    return None

def add_attributes_to_layer(list_of_attributes,layer_name):
    for full_attr_path in list_of_attributes:
        cmds.animLayer(layer_name, edit=True, attribute=full_attr_path)
    
async def import_animations(*args):
    if import_directory is None or not import_directory :
        cmds.confirmDialog(title='Error', message='Please browse a import_directory to import FBX files from', button='OK')
        return

    if len(xml_data_list)==0:
        cmds.confirmDialog(title='Error', message='Please choose an XML file', button='OK')
        return


    if fbx_files is None or len(fbx_files)==0:
        cmds.confirmDialog(title='Error', message='No FBX file found in the given import_directory', button='OK')
        return

    if root_group_selection is None:
        cmds.confirmDialog(title='Error', message='Please select the parent transform of the Root Joint of target character', button='OK')
        return

    if root_bone_selection is None:
        cmds.confirmDialog(title='Error', message='Please select the root joint of the target character', button='OK')
        return

    if facial_animation_target_selection is None:
        cmds.confirmDialog(title='Error', message='Please select target to apply facial animation to', button='OK')
        return


    global blendshape_node
    blendshape_node = get_blendshape_node(facial_animation_target_selection[0])


    load_fbx_plugin()
    create_time_editor_if_doesnt_exists()

    track_id=0
    create_composition()

    body_and_facial_animation_sources = []
    connected_xml_datas = {}
    cmds.currentUnit(time='ntscf') # 60 frames per second

    for fbx_file_name in fbx_files:
        await remove_keyframes(root_group_selection[0], False)  # Remove keyframes from the body
        await remove_keyframes(facial_animation_target_selection[0], True)  # Remove keyframes from the face
        file_name_without_extension = os.path.splitext(fbx_file_name)[0]
        parts = fbx_file_name.split('_')
        scene_group_take_name_from_fbx = '_'.join(parts[:4])

        connected_xml_data = [xml_data for xml_data in xml_data_list if
                              xml_data.file_name.startswith(file_name_without_extension)]

        if not connected_xml_data:
            print("WARNING ! : Couldn't find any usable data in XML for %s clip won't be cut !",file_name_without_extension)

        else:
            connected_xml_datas[file_name_without_extension] = connected_xml_data

        connected_json_file = [json_file for json_file in json_files if json_file.startswith(scene_group_take_name_from_fbx)]
        facial_anim_result=False

        if connected_json_file:
            connected_json_file = connected_json_file[0]
            full_json_path = os.path.join(import_directory,connected_json_file)

            facial_anim_result = await apply_given_json_file(full_json_path)

        full_path = os.path.join(import_directory,fbx_file_name)


        before_import_nodes = set(cmds.ls(dag=True, long=True))
        await import_single_fbx(os.path.join(import_directory,fbx_file_name))
        after_import_nodes = set(cmds.ls(dag=True, long=True))

        imported_nodes = after_import_nodes - before_import_nodes
        imported_nodes = list(imported_nodes)

        # TODO : if imported nodes is zero that means the same file is already in the scene.

        nodes = imported_nodes[0].split('|')

        root_node_of_imported = nodes[1]
        group_root_object = root_group_selection[0]

        await apply_body_animation(root_node_of_imported,group_root_object)


        source_ids= await create_track_and_editor_clip(file_name_without_extension,group_root_object,facial_anim_result)
        body_and_facial_animation_sources.append(source_ids)

        await remove_keyframes(root_group_selection[0],False) # Remove keyframes from the body
        await remove_keyframes(facial_animation_target_selection[0],True) # Remove keyframes from the face


        # await set_all_blendshapes_to_zero(facial_animation_target_selection[0])
        cmds.delete(root_node_of_imported)
    await create_tracks_from_sources(body_and_facial_animation_sources,connected_xml_datas)
    mute_all_tracks_in_composition(last_composition_name)
    cmds.refresh()


def on_button_click(*args):
    asyncio.run(import_animations())
        
if cmds.window('animation_transfer_window', exists=True):
    cmds.deleteUI('animation_transfer_window', window=True)
        
window = cmds.window('animation_transfer_window', title='Animotive Animation Transfer', resizeToFitChildren = True)
cmds.window(window,edit=True,sizeable=True)
cmds.columnLayout(adjustableColumn=True)

cmds.text(label='')
cmds.text(label='Select the import_directory which contains FBX and JSON files to import :')
cmds.textField('user_selected_import_directory_textField', editable=False)
cmds.button(label='Choose Import Directory', command=choose_import_directory_and_retrieve_files)

cmds.text(label='')
cmds.text(label='Select xml file :')
cmds.textField('user_selected_xml_text_field', editable=False)
cmds.button(label='Choose XML', command=import_xml)

cmds.text(label='')
cmds.text(label='Select the characters root group :')
cmds.textField('user_selected_root_group_textField', editable=False)
cmds.button(label='Select Target(Character) Root', command=get_selected_root_group_and_set_text_field)


cmds.text(label='')
cmds.text(label='Select the characters root joint :')
cmds.textField('user_selected_root_joint_textField', editable=False)
cmds.button(label='Select Character Root Joint', command=get_selected_root_joint_and_set_text_field)

cmds.text(label='')
cmds.text(label='Select target object to apply facial animation :')
cmds.textField('user_selected_graphics_group_text_field', editable=False)
cmds.button(label='Select Facial Animation Target', command=get_graphics_root_group_and_set_text_field)



cmds.text(label='')
cmds.button(label='Import', command=on_button_click)



cmds.showWindow(window)