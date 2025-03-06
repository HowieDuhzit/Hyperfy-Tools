<p align="center">
  <img src="extras/logo.png" alt="Hyperfy Tools Logo" width="150"/>
</p>

# [Hyperfy](https://github.com/hyperfy-xyz/hyperfy) Tools

Blender addon for creating and exporting assets for the Hyperfy platform.

## Features
- Create rigidbody objects with LODs and colliders
- Convert between Mixamo and VRM rigs
- Export GLB files with custom properties
- Add snap points for object placement
- Renamer for advanced batch object renaming (New in 1.5.0)
- Enhanced stability and performance (New in 1.4.3)
- Improved error handling and debugging (New in 1.4.3)

## Installation
1. Download the latest release
2. In Blender, go to Edit > Preferences > Add-ons
3. Click "Install" and select the downloaded file
4. Enable the addon by checking the box

### Theme Installation (Optional)
For the full cyberpunk experience:
1. Download [Hyperfy.blend](https://github.com/HowieDuhzit/HyperfyTools/releases/download/v1.4.0/Hyperfy.blend) and [Hyperfy.xml](https://github.com/HowieDuhzit/HyperfyTools/releases/download/v1.4.0/Hyperfy.xml)
2. In Blender, go to Edit > Preferences > Themes
3. Click "Install..." and select Hyperfy.xml for the UI theme
4. Open Hyperfy.blend and File > Defaults > Load Factory Settings
5. The theme will now be applied with custom splash screen and icons

## Usage
The tools can be found in the Hyperfy tab in the 3D View sidebar (N).

### Rigidbody Creation
- Select mesh objects to convert
- Set physics type and properties
- Create colliders (box, sphere, or mesh-based)
- Add LOD variants with naming convention (e.g., Cube_LOD0, Cube_LOD1)
- Add collision meshes with _COL suffix

### Rig Conversion
- Select an armature
- Convert between Mixamo and VRM naming conventions
- Maintains bone hierarchy and relationships

### Renamer
- Batch rename multiple selected objects at once
- Add or remove prefixes and suffixes
- Find and replace text in object names
- Convert case (uppercase, lowercase, title case)
- Add sequential numbering with customizable options
- Clean up special characters in object names

### Export
- Export single objects or entire scenes
- Preserves custom properties and hierarchy
- Supports batch export of multiple objects

## Links
- [Hyperfy Engine](https://hyperfy.xyz/)
- [GitHub](https://github.com/HowieDuhzit/HyperfyTools)
- [Blender Extensions](https://extensions.blender.org/author/25892/)
