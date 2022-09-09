import bpy
import random

### Constants ###
colors = {
    0: ["blue", (0.2549019607843137, 0.4117647058823529, 0.8823529411764706, 1)],
    1: ["violet", (0.5411764705882353, 0.16862745098039217, 0.8862745098039215, 1)],
    2: ["brown", (0.5450980392156862, 0.27058823529411763, 0.07450980392156863, 1)],
    3: ["green", (0.0, 0.5019607843137255, 0.0, 1)],
    4: ["yellow", (1.0, 1.0, 0.0, 1)],
    5: ["red", (0.803921568627451, 0.3607843137254902, 0.3607843137254902, 1)],
    6: ["white", (1.0, 1.0, 1.0, 1)],
    7: ["gray", (0.5019607843137255, 0.5019607843137255, 0.5019607843137255, 1)],
    8: ["purple", (0.5019607843137255, 0.0, 0.5019607843137255, 1)],
    9: ["dark blue", (0.09803921568627451, 0.09803921568627451, 0.4392156862745098, 1)],
    10: ["light green", (0.48627450980392156, 0.9882352941176471, 0.0, 1)],
    11: ["gold", (1.0, 0.8431372549019608, 0.0, 1)]
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
    
