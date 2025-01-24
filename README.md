# ⚡ HYPERFY TOOLS v1.0 ⚡

![Hyperfy Tools]([https://hyperfy.xyz/logo-icon.svg])

> A high-performance Blender addon for creating optimized physics objects and colliders for the Hyperfy engine.

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

1. Download `hyperfy_tools.zip`
2. Open Blender Preferences (Edit > Preferences)
3. Go to Add-ons tab
4. Click "Install" and select the downloaded zip
5. Enable the addon by checking the box

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

## 🔗 Links

- [Hyperfy Documentation](https://docs.hyperfy.io)
- [Report Issues](https://github.com/yourusername/hyperfy-tools/issues)
- [Discord Community](https://discord.gg/hyperfy)

---

<div align="center">

```ascii
 +-+-+-+-+-+-+ +-+-+-+-+-+
 |H|Y|P|E|R|F|Y|T|O|O|L|S|
 +-+-+-+-+-+-+ +-+-+-+-+-+
```

</div> 
