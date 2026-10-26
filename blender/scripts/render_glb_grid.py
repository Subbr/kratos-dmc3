"""Renderiza glbs lado a lado (com textura) em PNG. Uso: blender -b -P render_glb_grid.py -- <saida.png> <a.glb> [b.glb ...]"""
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
out, files = args[0], args[1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "FLAT"
scene.display.shading.color_type = "TEXTURE"
scene.render.resolution_x, scene.render.resolution_y = 400 * len(files), 400
world = bpy.data.worlds.new("w")
scene.world = world
world.color = (0.05, 0.05, 0.08)
x = 0.0
for path in files:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    pts = [o.matrix_world @ Vector(c) for o in new for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    size = max((hi - lo).x, (hi - lo).y, (hi - lo).z) or 1.0
    root = bpy.data.objects.new("root", None)
    scene.collection.objects.link(root)
    for o in new:
        if o.parent is None or o.parent not in new:
            o.parent = root
    root.location = -(lo + hi) / 2
    holder = bpy.data.objects.new("holder", None)
    scene.collection.objects.link(holder)
    root.parent = holder
    holder.scale = (1.0 / size,) * 3
    holder.location = (x, 0, 0)
    x += 1.2
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scene.collection.objects.link(cam)
cam.data.type = "ORTHO"
cam.data.ortho_scale = 1.2 * len(files)
cam.location = (1.2 * (len(files) - 1) / 2, -5, 0)
cam.rotation_euler = (1.5708, 0, 0)
scene.camera = cam
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
