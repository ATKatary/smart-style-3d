import os
import torch
import torchvision
import numpy as np

def _export_final(final_dir, mesh, losses, i):
    """
    Exports final obj after ith stylization iteration

    Inputs
        :final_dir: <str> path of directory to store final stylized mesh in
        :mesh: <Mesh> obj to store
        :losses: <tensor> of losses to store
        :i: <int> number of current stylization iteration
    """
    with torch.no_grad():
        mesh_name, ext = os.path.splitext(os.path.basename(mesh.path))
        mesh.export(os.path.join(final_dir, f"{mesh_name}_{i}_iters.obj"))

        torch.save(torch.tensor(losses), os.path.join(final_dir, "losses.pt"))

def _export_iters(iters_dir, rendered_images, i):
    """
    Inputs
        :iters_dir: <str> path of directory to store screenshots of the final stylized mesh in
        :rendered_images: <tensor> of screenshots of the mesh to store
        :i: <int> number of current stylization iteration
    """
    image_path = os.path.join(iters_dir, f"{i}_iters.jpg")
    torchvision.utils.save_image(rendered_images, image_path)