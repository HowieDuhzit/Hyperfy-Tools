# ⚡ HYPERFY TOOLS v1.1.0 ⚡

<div align="center">

```ascii
╔══════════════════════════════════════╗
║     H Y P E R F Y  ·  T O O L S     ║
╚══════════════════════════════════════╝
```

> A high-performance Blender addon for creating optimized physics objects and colliders for the Hyperfy engine.

</div>

## 📥 Installation

Latest build (V1.1) available for direct download:
- [Download hyperfy_tools_V1.1.zip](https://github.com/HowieDuhzit/Hyperfy-Tools/releases/tag/v1.1)

### System Requirements
- Blender 4.3.0+
- Compatible with all major OS platforms

## 🌟 Core Systems

### 📦 Physics
- **Rigidbody Types**
  - `STATIC` - Immovable collision anchors
  - `DYNAMIC` - Full physics simulation
  - `KINEMATIC` - Programmed movement patterns

### 🛡️ Collider Framework
- **Box Collider [BOX]**
  - Precision width/height/depth control
  - Optimal for architectural elements
  
- **Sphere Collider [SPH]**
  - Variable radius configuration
  - Perfect for projectiles/particles
  
- **Geometry Collider [GEO]**
  - 1:1 mesh precision
  - Ideal for complex static meshes
  
- **Simple Collider [SIM]**
  - Automated mesh optimization
  - Smart polygon reduction
  - Collision accuracy preservation
  - Performance-optimized for dynamic objects

### 🎮 Advanced Protocols
- **Collision Properties**
  - `CONVEX` mode for dynamic interactions
  - `CONCAVE` mode for static precision
  
- **Trigger System**
  - Non-physical interaction volumes
  - Event zone creation
  - Perfect for detection areas

### 🎨 Mesh Configuration
- **Shadow System**
  - Configurable shadow casting
  - Customizable shadow reception
  - Performance optimization options

### 💾 Export Protocols
- **Single Export Protocol**
  - Selected object export
  - Hierarchy preservation
  - Custom property retention
  
- **Batch Export Protocol**
  - Multi-object processing
  - Auto-centering algorithm
  - Individual GLB generation

### ⚡ Batch Operations
- **Multi-Rigidbody Creation**
  - Bulk physics setup
  - Hierarchy preservation
  - Automated collider generation
  - Mass property configuration

## 🚀 Installation

1. Download `hyperfy_tools_v1.1.0.zip`
2. Access Blender's Preferences (Edit > Preferences)
3. Navigate to Add-ons
4. Click "Install" - select `hyperfy_tools_v1.1.0.zip`
5. Activate by enabling "3D View: Hyperfy Tools"
6. Interface accessible in 3D View sidebar (Neural key: N)

> ⚠️ CRITICAL: Maintain zip integrity - Blender requires original package structure

## 🎯 Quick Boot Sequence

1. Initialize Hyperfy Tools in sidebar (N)
2. Select target mesh (optional)
3. Configure physics/collider parameters
4. Execute "CREATE RIGIDBODY"
5. Export via preferred protocol

## 🔧 Optimization Protocols

### Collider Selection
```
┌────────────┬─────────────────────────┐
│ BOX        │ Basic geometry          │
│ SPHERE     │ Spherical objects       │
│ GEOMETRY   │ Complex static meshes   │
│ SIMPLE     │ Optimized dynamics      │
└────────────┴─────────────────────────┘
```

### Performance Optimization
```
┌─────────────┬────────────────────┐
│ CONVEX      │ Physics optimal    │
│ SIMPLE      │ Reduced overhead   │
│ BOX/SPHERE  │ Maximum efficiency │
└─────────────┴────────────────────┘
```

### Export Guidelines
```
┌──────────┬───────────────────┐
│ SCENE    │ Connected assets  │
│ BATCH    │ Separate objects  │
│ COLLIDER │ Auto-hidden      │
└──────────┴───────────────────┘
```

## 🛠️ Technical Specifications

### Data Structure
```python
node: "rigidbody" | "collider" | "mesh"
type: "static" | "dynamic" | "kinematic"
collider: "box" | "sphere" | "geometry" | "simple"
convex: boolean
trigger: boolean
mass: float
```

### Hierarchy
```
RigidBody (Empty)
├── Mesh
│   ├── castShadow
│   └── receiveShadow
└── Collider
    ├── convex
    └── trigger
```

## 💫 Credits

Engineered by Howie Duhzit
For integration with Hyperfy Engine v1.1.0

---

<div align="center">

```ascii
╔═══════════════════════════════════════════╗
║  HYPERFY TOOLS - ENHANCE YOUR REALITY     ║
╚═══════════════════════════════════════════╝
```

</div> 
