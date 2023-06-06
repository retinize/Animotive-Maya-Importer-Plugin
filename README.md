# Animation Transfer Tool for Maya

This script provides a simple tool for transferring animations between different character rigs in Autodesk Maya. The script works by comparing hierarchies and transferring animation from a source rig to a target rig.

## Setup

1. Clone the repository or download the script file.
2. Open Autodesk Maya.
3. In the Script Editor, load the Python script file.

## Usage

The script opens a new window in Maya named "Animation Transfer". It contains several UI elements for easy usage.

### Select Target Root

Click on the "Select Target Root" button, then select the root object of the target rig in the Maya viewport. This is the rig you want to apply the animation to. The selected object's name will appear in the text field.

### Select Animative Export Root

Click on the "Select Animative Export Root" button, then select the root object of the source rig in the Maya viewport. This is the rig that already has the animation you want to transfer. The selected object's name will appear in the text field.

### Apply Animation

Click on the "Apply Animation" button to transfer the animation from the source rig to the target rig. This process may take a while depending on the complexity of the rigs and the length of the animation.

Note: If no objects or multiple objects are selected when selecting the roots, an error message will appear, prompting the user to select a single object.

## Features

- **Reset Rotations:** Resets the rotations of all animated objects to their initial state.

- **Parent Constraints Creation:** Creates parent constraints between corresponding objects in the source and target rigs, ensuring that the animation is transferred correctly.

- **Parent Constraints Deletion:** Deletes the parent constraints after the animation has been transferred, allowing the rigs to move independently again.

## Requirements

- Autodesk Maya

## Limitations

This script assumes that the naming conventions and hierarchies of the source and target rigs are similar. If the rigs have different naming conventions or hierarchies, the script may not work as expected.

## License

This project is licensed under the MIT License.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
