import clip
import torch
from tqdm import tqdm
from copy import deepcopy
from .utils import device
from render import Renderer
from torchvision import transforms
from .helpers.x2mesh_helpers import (
    _initiate,
    _construct_mask
)
from .helpers.report_helpers import (
    _export_final,
    _export_iters
)
from .test import test

torch.autograd.set_detect_anomaly(True)
### Global Constants ####
clip_model, preprocess = clip.load('ViT-B/32', device, jit=False)

### Functions ###
def x2mesh(args):
    """
    Runs the neural style field on the model and uses cosine similarity between different images of the mesh and a clip embedding of
    the prompt (or image) to learn an optimal stylization of the model

    Inputs
        :settings: <dict> of different settings (a set of disjoint sets)
                            1. initiation -> the arguments needed to intialize the process
                            2. render -> the arguments needed to render the mesh and retrive images
                            3. run -> the arguments needed to run the process 
    """
    loss, losses = 0, []
    norm_loss, norm_losses = 0.0, []

    norm_weight = 1.0
    rendered_images = None
    mesh, nsf, results_path, encodings, crop_cur, crop_update = _initiate(clip_model, preprocess, args)

    vertex_mask = _construct_mask(args.vertices_to_not_change, mesh)

    renderer = Renderer(mesh)
    optimizer = torch.optim.Adam(nsf.parameters(), args.lr, weight_decay=args.decay)
    
    activate_scheduler = args.lr_decay < 1 and args.decay_step > 0 and not args.lr_plateau
    if activate_scheduler:
        lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=args.decay_step, gamma=args.lr_decay)

    vertices = deepcopy(mesh.vertices)
    network_input = deepcopy(vertices)

    if args.symmetry == True: network_input[:, 2] = torch.abs(network_input[:, 2])
    if args.standardize == True: network_input = (network_input - torch.mean(network_input, dim=0)) / torch.std(network_input, dim=0)

    for i in tqdm(range(args.n_iter)):
        optimizer.zero_grad()
        _update_mesh(nsf, mesh, network_input, vertex_mask, vertices)
        rendered_images, loss, norm_loss = test(nsf, mesh, renderer, encodings, clip_model, optimizer, (loss, norm_loss), norm_weight, crop_update, args, i)
        
        losses.append(loss.item())
        norm_loss.append(norm_loss.item())
        if activate_scheduler: lr_scheduler.step()
        with torch.no_grad(): losses.append(loss.item())
        if args.decay_freq is not None and i % args.decay_freq == 0: norm_weight *= args.crop_decay

        if i % 100 == 0: _report(mesh, rendered_images, results_path, losses, i)
    _report(mesh, rendered_images, results_path, losses, i)
  
### Helper Functions ###
def _report(mesh, rendered_images, results_path, losses, i):
    """
    Reports the ith state of the mesh by storing the ith model state and different 
    rendered images of the mesh and stores it in results, while reporting the loss

    Inputs
        :mesh: <Mesh> representation of the object we are stylizing
        :rendered_images: <np.ndarray> of image renderings of the mesh
        :result_path: <str> of where to store the results
        :losses: <float> losses of the nueral style field based on clip embeddings
        :i: <int> the number of the curretn meshs state
    """
    final_dir, iters_dir = results_path
    _export_final(final_dir, mesh, losses, i)
    _export_iters(iters_dir, rendered_images, i)

def _update_mesh(nsf, mesh, network_input, vertex_mask, vertices):
    """
    Updates the mesh by computing a color and displacement for each vertex in the mesh

    Inputs
        :nsf: <NeuralStyleField> network used to stylize the mesh
        :mesh: <Mesh> to be stylized
        :network_input: <tensor> of mesh vertices
        :vertex_mask: <tensor> of mask for stylization control
        :vertices: <tensor> of mesh vertices
    """
    pred_rgb, pred_normal = nsf(network_input)
    pred_rgb = vertex_mask.to(device) * pred_rgb
    mesh.set_face_attributes_from_color(pred_rgb)
    mesh.vertices = vertices + vertex_mask * (mesh.vertex_normals * pred_normal)
