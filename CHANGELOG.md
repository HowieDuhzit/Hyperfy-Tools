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