import bpy
import random

### Constants ###
colors = {
    0: ["Red", (0.5, 0.0, 0.0, 1)],
    1: ["Brown", (0.23, 0.15, 0.05, 1)],
    2: ["Olive", (0.19, 0.19, 0.0, 1)],
    3: ["Yellow", (0.39, 0.34, 0.04, 1)],
    4: ["Lime Green", (0.29, 0.36, 0.10, 1)],
    5: ["Cyan", (0.10, 0.32, 0.375, 1)],
    6: ["White", (1.0, 1.0, 1.0, 1)],
    7: ["Purple", (0.22, 0.04, 0.27, 1)],
    8: ["Lavender", (0.33, 0.29, 0.39, 1)],
    9: ["Mint", (0.26, 0.4, 0.29, 1)],
    10: ["Beige", (0.4, 0.38, 0.30, 1)],
    11: ["Magenta", (0.36, 0.07, 0.35, 1)]
}

def assign_materials(mesh, k, faces, context, labels):
    """ Assigns a random colored material for each found segment """
    # clear all existing materials
    mesh.data.materials.clear()
    label_to_faces = {i: [] for i in range(len(set(faces)))}
    
    for i in range(len(faces)): label_to_faces[faces[i]].append(i)
    print(f"I found {len(faces)} labels!")

    for i in range(k):
        material = bpy.data.materials.new(''.join(['mat', mesh.name, str(i)]))
        material.diffuse_color = colors[i][1]
        mesh.data.materials.append(material)

        if len(context.scene.segments) <= i: segment = context.scene.segments.add()
        else: segment = context.scene.segments[i]

        segment.i = i
        segment.label = labels[i]
        segment.color = colors[i][0]
        segment.faces = "\n".join(str(j) for j in label_to_faces[i])
        segment.selected = True if segment.label == "function" else False

    for i, label in enumerate(faces):
        mesh.data.polygons[i].material_index = label
    
