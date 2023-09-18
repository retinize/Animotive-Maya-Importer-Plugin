import maya.cmds as cmds
import sys
import re
import os

fbx_files = None
directory = None
root_group_selection = None
root_bone_selection = None
created_parent_constraints = []
last_composition_name = ""


# ---- Body Retargeting ----

def delete_parent_constraints_recursive(obj):
    descendents = cmds.listRelatives(obj, allDescendents=True, fullPath=True,type='parentConstraint') or []
    if descendents:
        cmds.delete(descendents)


def apply_animation(animated_root,target_root):
    if not target_root:
        cmds.confirmDialog(title='Error', message='Please select a root of the target where you want the animation to be applied.', button='OK')
        return
    if not animated_root:
        cmds.confirmDialog(title='Error', message='Please select a root object of the animotive export', button='OK')
        return
    if not root_group_selection:
        cmds.confirmDialog(title='Error', message='Please select a root bone joint of the target', button='OK')
        return
    delete_parent_constraints_recursive(target_root)
    cmds.currentTime(0, edit=True)

    animated_children = cmds.listRelatives(animated_root, allDescendents=True, type='transform', path=True)
    animated_children.append(animated_root)
    target_children = cmds.listRelatives(target_root, allDescendents=True, type='joint', path=True)
    target_children.append(target_root)

    #reset_rotations(animated_children)
    create_parent_constraint(animated_children, target_children)
    clip_duration=0
    
    for child in animated_children:
        key_times = cmds.keyframe(child, q=True)
        if key_times is not None and is_list_zero(key_times)==False:
            clip_duration = key_times
            break
  
    cmds.playbackOptions(edit=True, animationStartTime=0)
    cmds.playbackOptions(edit=True, animationEndTime=clip_duration[-1])
    min_time = cmds.playbackOptions(edit=True, minTime=0)
    max_time = cmds.playbackOptions(edit=True, maxTime=clip_duration[-1])
    

    cmds.bakeResults(target_children, t=(min_time, max_time), simulation=True)

    delete_parent_constraint()


#def reset_rotations(object_list):
    #for obj in object_list:
        #cmds.setAttr(obj + '.rotateX', 0)
        #cmds.setAttr(obj + '.rotateY', 0)
        #cmds.setAttr(obj + '.rotateZ', 0)
        #cmds.setAttr(obj + '.rotate', 0, 0, 0)
        #cmds.setKeyframe(obj, attribute='rotate')
        
def is_list_zero(target_list):
    return(all(x == 0.0 for x in target_list))      

def create_parent_constraint(animated_children, target_children):
    for animated_child in animated_children:
        animated_child_name = animated_child.split(':')[-1]
        for target_child in target_children:
            if animated_child_name in target_child:
                is_root = target_child == root_bone_selection[0]
                
                if is_root:
                    print(target_child)
                    print(root_bone_selection[0])
                    
                constraint = None
                if is_root:
                    constraint = cmds.parentConstraint(animated_child, target_child,mo=False)
                else:
                    constraint = cmds.parentConstraint(animated_child, target_child,mo=False, st=['x', 'y', 'z'])
                created_parent_constraints.append(constraint)


def delete_parent_constraint():
    for constraint in created_parent_constraints:
        if cmds.objExists(constraint[0]):
            cmds.delete(constraint[0])
    del created_parent_constraints[:]


# ---- End of Body Retargeting ----


def load_fbx_plugin():
    plugin_name = "fbxmaya"
    if not cmds.pluginInfo(plugin_name, q=True, loaded=True):
        cmds.loadPlugin(plugin_name)

def choose_directory_and_retrieve_fbxes(*args):
    global fbx_files
    global directory
    directory = cmds.fileDialog2(dialogStyle=2, fileMode=3)
    
    if not directory:
        return []
        
    directory = directory[0]
    cmds.textField('user_selected_directory_textField', edit=True,text=directory)
    fbx_files = [f for f in os.listdir(directory) if f.lower().endswith('.fbx')]

def get_selected_root_group_and_set_text_field(*args):
    global root_group_selection
    root_group_selection = cmds.ls(selection=True, type='transform')

    if len(root_group_selection) != 1:
        root_group_selection = None
        cmds.textField('user_selected_root_group_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message="Please select the parent object of the character rig group", button='OK')
    else:
        cmds.textField('user_selected_root_group_textField', edit=True, text=root_group_selection[0])
        return root_group_selection

def get_selected_root_joint_and_set_text_field(*args):
    global root_bone_selection
    root_bone_selection = cmds.ls(selection=True, type='transform')

    if len(root_bone_selection) != 1:
        root_bone_selection = None
        cmds.textField('user_selected_root_joint_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message="Please select the character root Joint of the target character", button='OK')
    else:
        cmds.textField('user_selected_root_joint_textField', edit=True, text=root_bone_selection[0])
        return root_bone_selection
            

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


def create_track_and_editor_clip(clip_name,target_root,track_id):
    all_children = cmds.listRelatives(target_root, allDescendents=True, type='joint', path=True)
    
    if len(all_children)==0:
        print("No object was found")
        return

    temp = ";".join(all_children)
    
    
    source_id = cmds.timeEditorAnimSource(clip_name,ao= temp, addRelatedKG=True, removeSceneAnimation=True, includeRoot=True, recursively=True)
    cmds.timeEditorTracks(path=last_composition_name,addTrack=-1,e=1)
    print(last_composition_name+"|track"+str(track_id))
    cmds.timeEditorClip(clip_name,track=last_composition_name+"|track"+str(track_id), animSource=source_id, startTime=1) 

def legalize_string(name):
    legal_name = ''.join(ch if ch.isalnum() else '_' for ch in name)
    return legal_name

def create_composition():
    global last_composition_name 
    last_composition_name = 'MyComposition'+get_last_composition_index()
    
    if not cmds.objExists(last_composition_name):
        cmds.timeEditorComposition(last_composition_name) 

def remove_keyframes(root_object):
    objects = cmds.listRelatives(root_object, allDescendents=True, fullPath=True)
    for current_object in objects:
        cmds.cutKey(current_object, clear=True) 

def import_fbxes(*args):

    if directory is None or not directory :
        cmds.confirmDialog(title='Error', message='Please browse a directory to import FBX files from', button='OK')
        return
    
    if fbx_files is None or len(fbx_files)==0:
        cmds.confirmDialog(title='Error', message='No FBX file found in the given directory', button='OK')
        return
    
    if root_group_selection is None:
        cmds.confirmDialog(title='Error', message='Please select the parent transform of the Root Joint of target character', button='OK')
        return
    
    if root_bone_selection is None:
        cmds.confirmDialog(title='Error', message='Please select the root joint of the target character', button='OK')
        return
    
    if not cmds.pluginInfo("fbxmaya", q=True, loaded=True):
        cmds.loadPlugin("fbxmaya")
     
    load_fbx_plugin()
    create_time_editor_if_doesnt_exists()
    
    track_id=1
    create_composition()
    
    imported_node_roots=[]
    
    for fbx_path in fbx_files:
        remove_keyframes(root_group_selection[0])
        full_path = os.path.join(directory,fbx_path)
        file_name_without_extension = os.path.splitext(fbx_path)[0]
                
        before_import_nodes = set(cmds.ls(dag=True, long=True))
        cmds.FBXImport("-f",os.path.join(directory,fbx_path),'-caller "FBXMayaTranslator" -importFormat "fbx"')
        after_import_nodes = set(cmds.ls(dag=True, long=True))
                
        imported_nodes = after_import_nodes - before_import_nodes
        imported_nodes = list(imported_nodes)
        nodes = imported_nodes[0].split('|')
            
        root_node_of_imported = nodes[1]
        group_root_object = root_group_selection[0]
        
        apply_animation(root_node_of_imported,group_root_object)
        create_track_and_editor_clip(file_name_without_extension,group_root_object,track_id)
        track_id +=1
        remove_keyframes(root_group_selection[0])
        imported_node_roots.append(root_node_of_imported)
    cmds.delete(root_node_of_imported)
        
    
window = cmds.window('animation_transfer_window', title='Animotive Animation Transfer', resizeToFitChildren = True)
cmds.window(window,edit=True,sizeable=True)
cmds.columnLayout(adjustableColumn=True)


cmds.text(label='')
cmds.text(label='Select the directory which contains FBX files to import :')
cmds.textField('user_selected_directory_textField', editable=False)
cmds.button(label='Choose FBX Directory', command=choose_directory_and_retrieve_fbxes)

cmds.text(label='')
cmds.text(label='Select the characters root group :')
cmds.textField('user_selected_root_group_textField', editable=False)
cmds.button(label='Select Target(Character) Root', command=get_selected_root_group_and_set_text_field)


cmds.text(label='')
cmds.text(label='Select the characters root joint :')
cmds.textField('user_selected_root_joint_textField', editable=False)
cmds.button(label='Select Character Root Joint', command=get_selected_root_joint_and_set_text_field)

cmds.text(label='')
cmds.button(label='Import', command=import_fbxes)

cmds.showWindow(window)