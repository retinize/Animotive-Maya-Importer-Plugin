import maya.cmds as cmds
import sys
import re
import os
fbx_files = None
directory = None
user_selection = None

def choose_directory_and_retrieve_fbxes(*args):
    global fbx_files
    global directory
    directory = cmds.fileDialog2(dialogStyle=2, fileMode=3)
    
    if not directory:
        return []
        
    directory = directory[0]
    cmds.textField('user_selected_directory_textField', edit=True,text=directory)
    fbx_files = [f for f in os.listdir(directory) if f.lower().endswith('.fbx')]

def get_selected_object_and_set_textField(*args):
    global user_selection
    user_selection = cmds.ls(selection=True, type='transform')

    if len(user_selection) != 1:
        user_selection = None
        cmds.textField('user_selected_root_bone_textField', edit=True, text='')
        cmds.confirmDialog(title='Error', message="Please select the parent object of the character rig group", button='OK')
    else:
        cmds.textField('user_selected_root_bone_textField', edit=True, text=user_selection[0])
        return user_selection

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


def get_current_selection():
    selection = cmds.ls(selection=True)

    if selection is None or len(selection)==0:
        print("Please choose the source of animation first !")
        sys.exit()
    
    all_children = cmds.listRelatives(selection, allDescendents=True, type='joint', path=True)
    
    if len(all_children)==0:
        print("No object was found")
        sys.exit()
    
    try:
        cmds.workspaceControl('Control')
        cmds.timeEditorPanel()
    except RuntimeError as e:
        if "Object's name" not in str(e):
            print("Error:", e)
        else:
            print("Time Editor already exists")
    

def create_composition():
    last_composition_name = 'MyComposition'+get_last_composition_index()
    cmds.timeEditorComposition(last_composition_name)

    temp = ";".join(all_children)

    cmds.timeEditorAnimSource("anim_Clip1",ao= temp, addRelatedKG=True, removeSceneAnimation=True, includeRoot=True, recursively=True)
    
    

def import_fbxes(*args):
    if directory is None or not directory :
        cmds.confirmDialog(title='Error', message='Please browse a directory to import FBX files from', button='OK')
        return
    
    if fbx_files is None or len(fbx_files)==0:
        cmds.confirmDialog(title='Error', message='No FBX file found in the given directory', button='OK')
        return
    
    if user_selection is None:
        cmds.confirmDialog(title='Error', message='Please select the root of the target character', button='OK')
        return
    
    if not cmds.pluginInfo("fbxmaya", q=True, loaded=True):
        cmds.loadPlugin("fbxmaya")
    
    for fbx_path in fbx_files:
        full_path = os.path.join(directory,fbx_path)
        file_name_without_extension = os.path.splitext(fbx_path)[0]
        cmds.file(full_path, i=True, type="FBX", preserveReferences=True,ns=file_name_without_extension)
            
    

    
    # check if a directory is selected
    # check if the character root is selected
    print("Import is called")
    
    
window = cmds.window('animation_transfer_window', title='Animotive Animation Transfer', resizeToFitChildren = True)
cmds.window(window,edit=True,sizeable=True)
cmds.columnLayout(adjustableColumn=True)


cmds.text(label='')
cmds.text(label='Select the directory which contains FBX files to import :')
cmds.textField('user_selected_directory_textField', editable=False)
cmds.button(label='Choose FBX Directory', command=choose_directory_and_retrieve_fbxes)

cmds.text(label='')
cmds.text(label='Select the characters root :')
cmds.textField('user_selected_root_bone_textField', editable=False)
cmds.button(label='Select Target(Character) Root', command=get_selected_object_and_set_textField)

cmds.text(label='')
cmds.button(label='Import', command=import_fbxes)

cmds.showWindow(window)