import bpy

depsgraph = bpy.context.evaluated_depsgraph_get()

for obj in bpy.data.objects:
    if obj.type != "MESH":
        continue
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(eval_obj, depsgraph=depsgraph)
    edges = len(mesh.edges)
    verts = len(mesh.vertices)
    polys = len(mesh.polygons)
    print(
        f"{obj.name}: verts={verts} edges={edges} polys={polys} "
        f"mat={obj.material_slots[0].material.name if obj.material_slots else None}"
    )
    bpy.data.meshes.remove(mesh)

# Check geometry nodes for line/curve output
for ng in bpy.data.node_groups:
    if ng.type != "GEOMETRY":
        continue
    print(f"Node group: {ng.name}")
    for node in ng.nodes:
        print(f"  {node.name} ({node.type})")
