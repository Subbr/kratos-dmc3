"""Importa um glTF e imprime um resumo (armature, malhas, ações). Uso:
blender -b -P blender/scripts/inspect_gltf.py -- <arquivo.glb> [saida.blend]
"""
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args[0])

arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
print("RESUMO armatures:", [(a.name, len(a.data.bones)) for a in arms])
print("RESUMO malhas:", len(meshes), "vértices:", sum(len(m.data.vertices) for m in meshes))
print("RESUMO ações:", len(bpy.data.actions))
max_infl = 0
for m in meshes:
    for v in m.data.vertices:
        max_infl = max(max_infl, sum(1 for g in v.groups if g.weight > 0))
print("RESUMO max ossos por vértice:", max_infl)
if len(args) > 1:
    bpy.ops.wm.save_as_mainfile(filepath=args[1])
    print("RESUMO salvo:", args[1])
