from os import listdir
from .utils import check_mesh
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
from os.path import isfile, join, isdir

def get_valid_models(dir_path, models = {}, text2mesh_path = "../text2mesh"):
    """
    Fetches all the available models in the directory given

    Inputs
        :dir_path: <str> to the directory containing model directories and model files
    
    Outputs
        <dict> from model name to model path
    """
    for filename in listdir(dir_path):
        file_path = f"{dir_path}/{filename}"
        if isfile(file_path):
            if ".obj" == filename[-4:]:
                try: 
                    check_mesh(file_path, text2mesh_path)
                    models[filename[:-4]] = file_path
                except: print(f"\033[91mFail[{file_path} Deprecated]\033[0m")
                
        elif isdir(file_path):
            models = get_valid_models(file_path, models, text2mesh_path)
    print(f"Found {len(models)} working models in {dir_path}")
    return models

def select_model(models: dict):
    """
    Helps user know which models are available and select which one to use

    Inputs
        :models: <dict> of model name to path

    Outputs
        <str> path to selected model
    """
    print(f"The available models are:\n{list(models.keys())}")
    selected_model = input("Name of model you want to use: ")
    return selected_model, models[selected_model]

def display(output_dir, obj, n_iter):
    """
    Displays the first and last iteration
    
    Inputs
        :output_dir: <str> the directory contianing the output files
        :obj: <str> the name of the object to display results of
        :n_iter: the number of iteration of the last result
    """
    f, plot = plt.subplots(2, 1, figsize=(12, 5))
    before_image = mpimg.imread(f"{output_dir}/{obj}_iters/iter_0.jpg")
    after_image = mpimg.imread(f"{output_dir}/{obj}_iters/iter_{(n_iter // 100) * 100}.jpg")
    plot[0].imshow(before_image)
    plot[1].imshow(after_image)
    plt.show()