"""Retrato do Kratos (glb do GoW1) numa pose de animação, fundo transparente, para as artes dos menus (T50).

Uso: blender -b -P render_kratos.py -- <glb> <saida.png> <animação> <fração 0–1> <largura> <altura> [ângulo° [zoom]]
"""
import math
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
glb, out, anim, frac, w, h = args[0], args[1], args[2], float(args[3]), int(args[4]), int(args[5])
angle = float(args[6]) if len(args) > 6 else 25.0
zoom = float(args[7]) if len(args) > 7 else 1.0

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
scene = bpy.context.scene
arm = next(o for o in scene.objects if o.type == "ARMATURE")
act = bpy.data.actions.get(anim) or next((a for a in bpy.data.actions if a.name.split(" ")[-1] == anim), None)
if act:
    arm.animation_data_create()
    arm.animation_data.action = act
    if hasattr(arm.animation_data, "action_slot") and act.slots:
        arm.animation_data.action_slot = act.slots[0]
    f0, f1 = act.frame_range
    scene.frame_set(int(round(f0 + (f1 - f0) * frac)))
bpy.context.view_layer.update()

# caixa do corpo deformado para enquadrar
pts = []
dg = bpy.context.evaluated_depsgraph_get()
for o in scene.objects:
    if o.type == "MESH":
        me = o.evaluated_get(dg).to_mesh()
        pts += [o.matrix_world @ v.co for v in me.vertices]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
center, size = (lo + hi) / 2, max((hi - lo).x, (hi - lo).y, (hi - lo).z)

scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
scene.render.film_transparent = True
scene.render.resolution_x, scene.render.resolution_y = w, h
world = bpy.data.worlds.new("w"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[1].default_value = 0.35

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scene.collection.objects.link(cam); scene.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = size * 1.1 / zoom
a = math.radians(angle)
dist = size * 3
# o glb do gowb é Y para cima no Blender após o import (Z para cima); câmera de frente (−Y) girada por "angle"
cam.location = center + Vector((math.sin(a) * dist, math.cos(a) * dist, size * 0.05))  # o Kratos olha para +Y
direction = center - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

# PS2: sem sombreamento confiável (normais facetadas) → textura como emissão, como o jogo original desenha
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not bsdf:
        continue
    src = bsdf.inputs["Base Color"].links[0].from_socket if bsdf.inputs["Base Color"].links else None
    if src:
        nt.links.new(src, bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 0.85

def light(name, kind, energy, color, loc):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, kind))
    l.data.energy = energy; l.data.color = color
    l.location = loc; scene.collection.objects.link(l)
    l.rotation_euler = (center - l.location).to_track_quat("-Z", "Y").to_euler()
light("key", "SUN", 1.0, (1.0, 0.95, 0.9), center + Vector((-dist, dist, dist)))
light("rim", "SUN", 4.0, (1.0, 0.25, 0.15), center + Vector((dist, -dist * 0.5, dist * 0.3)))

scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("ok", out, act.name if act else None, size)
