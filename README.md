# Hyperfy Tools for Blender

A Blender addon that provides tools for creating and exporting rigidbody objects for the Hyperfy platform, plus utilities for converting between different character rig formats.

## Features

### Rigidbody Creation
- Create rigidbody objects with mesh and collider components
- Support for different physics types:
  - Dynamic
  - Static
  - Kinematic
- Multiple collider options:
  - Box
  - Sphere
  - Simple (auto-simplified mesh)
  - Full geometry
- Batch creation for multiple objects
- Customizable mass and collision properties
- Shadow casting/receiving options

### Rig Conversion
- Convert between Mixamo and VRM rig formats
- One-click automatic bone renaming
- Support for:
  - Full body bones
  - Complete finger chains
  - Eye bones
  - All standard naming conventions
- Preserves bone hierarchy and transformations
- Smart UI that only appears when working with armatures

### Export Tools
- Export single objects as GLB
- Batch export multiple objects
- Preserves all custom properties
- Maintains hierarchy and transformations

## Installation

1. Download the latest release
2. In Blender, go to Edit > Preferences > Add-ons
3. Click "Install" and select the downloaded zip file
4. Enable the addon by checking the box

## Usage

### Rigidbody Creation
1. Select an object (optional)
2. Open the Hyperfy Tools panel in the 3D View sidebar (N)
3. Configure physics, mesh, and collider settings
4. Click "Create Rigidbody" or "Create Multiple Rigidbodies"

### Rig Conversion
1. Select an armature
2. Find the Rig Converter panel in the sidebar
3. Choose conversion direction (Mixamo → VRM or VRM → Mixamo)
4. Click to convert

### Export
1. Select object(s) to export
2. Use "Export Object" for single objects
3. Use "Export All Objects" for batch export

## New in Version 1.3.0

- Added Rig Converter panel for Mixamo/VRM conversion
- Improved property management with PropertyGroup
- Updated operator naming to follow Blender conventions
- Better code organization and registration
- See [CHANGELOG.md](CHANGELOG.md) for full details

## Requirements

- Blender 2.93 or newer
- GLB export capability (included in default Blender)

## Development

Properties are now accessed through the PropertyGroup:
```python
props = context.scene.hyperfy_props
props.physics_type
props.mass
props.collider_type
```

Operator names have changed to follow Blender conventions:
- `object.create_rigidbody` (was `hyperfy.create_rigidbody`)
- `object.export_glb` (was `hyperfy.export_glb`)
- `object.mixamo_to_vrm`
- `object.vrm_to_mixamo`

