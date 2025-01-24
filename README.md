# ⚡ HYPERFY TOOLS v1.0 ⚡

![Hyperfy Tools](hyperfy_logo.png)

> A high-performance Blender addon for creating optimized physics objects and colliders for the Hyperfy engine.

## 📥 Download

The latest release (v1.0) is available as a ready-to-install Blender addon:
- [Download hyperfy_tools_v1.0.zip](https://github.com/HowieDuhzit/Hyperfy-Tools/releases/tag/v1)

## 🌟 Features

### 📦 Physics System
- **Rigidbody Creation**
  - Static (non-moving collision objects)
  - Dynamic (physics-driven objects)
  - Kinematic (animated collision objects)
  - Customizable mass properties

### 🛡️ Collider Types
- **Box Collider**
  - Adjustable width/height/depth
  - Perfect for simple geometric shapes
  
- **Sphere Collider**
  - Adjustable radius
  - Ideal for rounded objects
  
- **Geometry Collider**
  - Uses exact mesh shape
  - Best for complex static objects
  
- **Simple Collider**
  - Automated mesh simplification
  - Optimized for performance
  - Maintains collision accuracy
  - Perfect for complex dynamic objects

### 🎮 Advanced Options
- **Convex/Concave Toggle**
  - Convex for dynamic-dynamic collisions
  - Concave for complex static shapes
  
- **Trigger Volumes**
  - Create non-physical trigger zones
  - Perfect for interaction areas

### 💾 Export System
- **Scene Export**
  - Export entire scene as single GLB
  - Maintains hierarchies
  - Preserves custom properties
  
- **Batch Export**
  - Export multiple objects
  - Auto-centers each object
  - Separate GLB per object
  - Perfect for kit-bashing

## 🚀 Installation

1. Download `hyperfy_tools_v1.0.zip` from the releases page
2. Open Blender Preferences (Edit > Preferences)
3. Go to Add-ons tab
4. Click "Install" and select `hyperfy_tools_v1.0.zip`
5. Enable the addon by checking "3D View: Hyperfy Tools"
6. The tools will appear in the 3D View sidebar (press N)

> ⚠️ Note: Do not unzip the file - Blender needs the original zip for installation

## 🎯 Quick Start

1. Open the Hyperfy Tools panel in the 3D View sidebar (N)
2. Select an object (optional)
3. Choose physics and collider settings
4. Click "CREATE RIGIDBODY"
5. Export using preferred method

## 🔧 Usage Tips

### Optimal Collider Selection
- **Box**: Use for basic shapes (cubes, buildings)
- **Sphere**: Best for rounded objects (balls, planets)
- **Geometry**: Use for detailed static objects
- **Simple**: Perfect for performance-critical dynamic objects

### Performance Optimization
- Use convex colliders when possible
- Simple colliders reduce physics calculations
- Box and sphere colliders are most efficient

### Export Guidelines
- Scene export for connected objects
- Batch export for separate assets
- Colliders are automatically hidden in export

## 🛠️ Technical Details

### Property Types
```python
node: "rigidbody" | "collider"
type: "static" | "dynamic" | "kinematic"
collider: "box" | "sphere" | "geometry" | "simple"
convex: boolean
trigger: boolean
```

### File Structure
```
RigidBody (Empty)
├── Mesh
└── Collider
```

## 💫 Credits

Created by Howie Duhzit
For use with the Hyperfy Engine

---

<div align="center">

```ascii
 +-+-+-+-+-+-+ +-+-+-+-+-+
 |H|Y|P|E|R|F|Y|T|O|O|L|S|
 +-+-+-+-+-+-+ +-+-+-+-+-+
```

</div> 
