"""Export blend to GLB with geometry nodes realized for web."""
import bpy
import os

blend_path = bpy.data.filepath
out_dir = os.path.join(os.path.dirname(blend_path), "assets")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "nettside.glb")


def insert_realize_instances(ng):
    if not ng or ng.type != "GEOMETRY":
        return
    output = None
    for node in ng.nodes:
        if node.type == "GROUP_OUTPUT":
            output = node
            break
    if not output:
        return

    # Skip if already realized
    for node in ng.nodes:
        if node.type == "REALIZE_INSTANCES":
            return

    realize = ng.nodes.new("GeometryNodeRealizeInstances")
    realize.location = (output.location.x - 200, output.location.y)

    geometry_input = None
    for link in ng.links:
        if link.to_node == output and link.to_socket.name == "Geometry":
            geometry_input = link
            break

    if not geometry_input:
        return

    from_socket = geometry_input.from_socket
    ng.links.remove(geometry_input)
    ng.links.new(from_socket, realize.inputs["Geometry"])
    ng.links.new(realize.outputs["Geometry"], output.inputs["Geometry"])


def style_materials():
    """Pitch-black main sphere; dots styled in the web viewer."""
    body = bpy.data.materials.get("Material.002")
    if body and body.node_tree:
        bsdf = None
        for node in body.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                bsdf = node
                break
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
            bsdf.inputs["Roughness"].default_value = 1.0
            bsdf.inputs["Metallic"].default_value = 0.0
            emission = bsdf.inputs.get("Emission") or bsdf.inputs.get("Emission Color")
            if emission:
                emission.default_value = (0.0, 0.0, 0.0, 1.0)
            emission_strength = bsdf.inputs.get("Emission Strength")
            if emission_strength:
                emission_strength.default_value = 0.0


for ng in bpy.data.node_groups:
    if ng.type == "GEOMETRY":
        insert_realize_instances(ng)

style_materials()

depsgraph = bpy.context.evaluated_depsgraph_get()

mesh_objects = [obj for obj in bpy.data.objects if obj.type == "MESH"]
converted = []

for obj in mesh_objects:
    eval_obj = obj.evaluated_get(depsgraph)
    new_mesh = bpy.data.meshes.new_from_object(eval_obj, depsgraph=depsgraph)

    if len(new_mesh.vertices) == 0:
        bpy.data.meshes.remove(new_mesh)
        continue

    obj.data = new_mesh
    obj.modifiers.clear()
    converted.append(obj)

# Remove empty mesh objects
for obj in mesh_objects:
    if obj not in converted and len(obj.data.vertices) == 0:
        bpy.data.objects.remove(obj, do_unlink=True)

bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format="GLB",
    use_selection=False,
    export_apply=True,
)

print(f"Exported {len(converted)} mesh object(s) to {out_path}")
