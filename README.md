# Animotive Animation Transfer Tools for Maya

# Requirements

- Autodesk Maya
- Python (python 3 and above)


## 1. Body Animation Transfer
This script provides a simple tool for transferring animations between different character rigs in Autodesk Maya. The script works by comparing hierarchies and transferring animation from a source rig to a target rig.

### Setup

1. Clone the repository or download the script file.
2. Open Autodesk Maya.
3. In the Script Editor, load the Python script file.

### Usage

The script opens a new window in Maya named "Animotive Animation Transfer". It contains several UI elements for easy usage.

#### Select Target Root

Click on the "Select Target Root" button, then select the root object of the target rig in the Maya viewport. This is the rig you want to apply the animation to. The selected object's name will appear in the text field.

#### Select Animotive Export Root

Click on the "Select Animotive Export Root" button, then select the root object of the source rig in the Maya viewport. This is the rig that already has the animation you want to transfer. The selected object's name will appear in the text field.

#### Apply Animation

Click on the "Apply Animation" button to transfer the animation from the source rig to the target rig. This process may take a while depending on the complexity of the rigs and the length of the animation.

Note: If no objects or multiple objects are selected when selecting the roots, an error message will appear, prompting the user to select a single object.

### Features

- **Reset Rotations:** Resets the rotations of all animated objects to their initial state.

- **Parent Constraints Creation:** Creates parent constraints between corresponding objects in the source and target rigs, ensuring that the animation is transferred correctly.

- **Parent Constraints Deletion:** Deletes the parent constraints after the animation has been transferred, allowing the rigs to move independently again.
- **Time Reset:** Resets the current time to 0 before starting any operation.


## 2. Face Animation Transfer

This is a Maya script that aids in transferring face animation from a JSON file to a character within Maya.

### Usage

To use this script:

1. Open the script in the Maya script editor.
2. Execute the script. This will open a GUI with two buttons.
3. In Maya, select the root of the target model, then press the "Select" button in the GUI.
4. Press the "Apply Animation" button in the GUI to apply the face animation from a JSON file to your character.

### Description of Functions

The script contains the following functions:

- `select_target_root(*args)`: This function sets the root of the target model.
- `get_blendshape_node_from_geo()`: This function retrieves blendshapes attached to the selected target root.
- `set_playback_speed()`: This function sets the playback speed based on the number of frames in the facial animation.
- `set_keyframes_from_json(*args)`: This function reads the JSON file and applies the facial animation to the target model.

### Note

The JSON file should contain information about the facial animation, including the blendshapes used and their values at each frame.
