"""Renderiza OBJs lado a lado (frente e perfil) em PNG. Uso: blender -b -P render_obj.py -- <saida.png> <a.obj> [b.obj ...]"""
import math
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
out, objs = args[0], args[1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "RANDOM"
scene.render.resolution_x, scene.render.resolution_y = 1600, 900
for k, path in enumerate(objs):
    bpy.ops.wm.obj_import(filepath=path, forward_axis="NEGATIVE_Z", up_axis="Y")
    for o in bpy.context.selected_objects:
        o.location.x += k * 140
        if k % 2 == 1:
            o.rotation_euler.z = math.radians(90)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scene.collection.objects.link(cam)
cam.data.type = "ORTHO"
cam.data.ortho_scale = 140 * len(objs) + 60
cam.location = (70 * (len(objs) - 1), -600, 95)
cam.rotation_euler = (math.radians(90), 0, 0)
scene.camera = cam
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
