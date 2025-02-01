bl_info = {
    "name": "Hyperfy Tools",
    "author": "Hyperfy",
    "version": (1, 3, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Hyperfy",
    "description": "Tools for preparing models for Hyperfy",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

from . import HyperfyTools

def register():
    HyperfyTools.register()

def unregister():
    HyperfyTools.unregister()

if __name__ == "__main__":
    register()
