# Changelog

All notable changes to the Hyperfy Tools addon will be documented in this file.

## [1.3.0] - 2024-03-19

### Added
- New Rig Converter panel for converting between Mixamo and VRM rigs
- One-click automatic bone renaming system
- Support for full body, finger, and eye bones
- Smart UI that only shows when armature is selected

### Changed
- Consolidated all addon properties into a single PropertyGroup
- Updated operator naming to follow Blender conventions:
  - `hyperfy.create_rigidbody` → `object.create_rigidbody`
  - `hyperfy.export_glb` → `object.export_glb`
  - etc.
- Improved property access throughout codebase
- Cleaner registration/unregistration process

### Removed
- Stray Scene ID properties
- Unused image files from addon package
- Legacy operator naming conventions

## [1.2.0] - 2024-02-15

### Added
- Batch export functionality for multiple objects
- Export all visible top-level objects as separate GLB files
- Support for exporting object hierarchies
- New export options panel with clear instructions

### Changed
- Improved GLB export to preserve custom properties
- Better handling of object hierarchies during export
- Enhanced error reporting for failed exports

## [1.1.0] - 2024-01-20

### Added
- Multiple collider type options:
  - Box collider
  - Sphere collider
  - Simple (auto-simplified) collider
  - Full geometry collider
- Batch rigidbody creation for multiple objects
- Support for maintaining object hierarchies

### Changed
- Improved collider generation algorithm
- Better handling of nested objects
- Enhanced UI with cyberpunk styling

### Fixed
- Issue with collider scaling
- Parent-child relationship preservation
- Material handling during collider creation

## [1.0.0] - 2023-12-01

### Initial Release
- Basic rigidbody creation functionality
- Physics type support (dynamic, static, kinematic)
- Custom property support for Hyperfy engine
- GLB export capability
- Shadow casting/receiving options
- Mass and collision properties
- Basic UI in 3D View sidebar

## [1.3.2] - 2024-03-XX

### Changed
- Changed default collider type from 'box' to 'geometry'
- Changed default convex setting to off
- Snap points now display as small spheres instead of axes
- Rigidbodies are now created in the same collection as their source meshes
- Improved world space position handling for parented objects when creating rigidbodies

### Fixed
- Fixed rigidbody type dropdown not updating custom properties in Details menu
- Fixed location issues when creating rigidbodies from parented meshes
- Fixed parent hierarchy preservation when creating rigidbodies

## [1.3.3] - 2024-03-19

### Added
- Multiple snap points can now be created at once by selecting multiple vertices
- Snap points can now be placed at selected vertex locations in edit mode
- Sequential naming for snap points (SnapPoint.001, SnapPoint.002, etc.)

### Changed
- Improved snap point placement accuracy with better world space transformation
- Enhanced snap point parenting to preserve world position when parenting to rigidbody
- Updated snap point feedback message to show number of points created
- Increased snap point sphere size for better visibility (0.1m → 0.2m)
- Moved snap points section above export section in UI for better workflow
- Improved mode handling when creating snap points in edit mode

### Fixed
- Fixed snap point positioning when parenting to rigidbody objects
- Fixed vertex location calculation in world space
- Fixed context issues when switching between edit and object modes
- Fixed mode restoration when creating snap points in edit mode

## [1.3.4] - 2024-03-XX

### Changed
- Adjusted LOD distances to be more appropriate for world size (200) and max camera distance (75)
  - LOD0: 25 units (closest, highest detail)
  - LOD1: 50 units
  - LOD2: 75 units (furthest, lowest detail)
- Improved rigidbody details UI to show when any part of hierarchy is selected
- Added live LOD distance editing in rigidbody details panel

### Fixed
- Improved naming convention consistency:
  - Main object: "Cube"
  - Collider: "CubeCollider"
  - LOD empty: "CubeLOD"
  - LOD meshes: "CubeMeshLOD0", "CubeMeshLOD1", etc.
- Fixed issue with COL objects creating separate rigidbodies
- Improved LOD grouping and sorting logic
- Fixed collider parenting when using COL objects
- Better handling of object naming and hierarchy creation
- Fixed rigidbody details not showing when selecting LOD or mesh objects

### Added
- Support for using existing COL objects as colliders
- Automatic detection and grouping of LOD variants
- Smarter base name detection for object groups
- Live editing of LOD distances in rigidbody details panel
- Rigidbody details now visible when selecting any part of the hierarchy

## [Previous Versions]
... 