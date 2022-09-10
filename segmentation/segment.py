import os
import cupy as cp
import numpy as np
import scipy.sparse.linalg
from face_graph import FaceGraph
from scipy.cluster.vq import kmeans2

def segment_mesh(mesh, model_loc, k = None):
    """
    Segments a mesh as follows:
        1. Converts mesh into a face graph, where 
            - each node is a face 
            - faces have edges between them iff they are adjacent 
            - weights of the edge between fi and fj = w(fi, fj) = δ * (geodisc(fi, fj)) / avg_geodisc + (1 - δ) * (ang_dist(fi, fj)) / avg_ang_dist
                - ang_dist(fi, fj) = η * (1 - cos(α(fi, fj))); η = 1 for α >= 180 and η -> 0 for α < 180
                - geodisc(fi, fj) = distance from center of fi to center of fj
        2. We compute similarity matrix M
            (How Katz and Tal did it) 
            Decide on k faces (f1, f2, ..., fk) to be the 'centroid nodes' of the graph
            For each node we compute the probability that it belongs to class k 
                - P_j(fi) = [1/w(fi, fj)] / [1/w(fi, f1) + 1/w(fi, f2) + ... + 1/w(fi, fk)]

            (How Liu and Zhang did it) 
            For each pair of nodes (fi, fj) we compute the similarity as 
                - Sim(fi, fj) = e^(-w(fi, fj) / [2 * (avg_w) ** 2]) if w(fi, fj) != inf & fi != fj
                              = 0 if w(fi, fj) == inf
                              = 1 if fi == fj
        3. Compute normal Laplacian of M, L
            - L = sqrt(D).T * M.T * sqrt(D); D is degree matrix of the face graph
        4. We compute eigenvalues and vectors of L
        5. We preform K-means clustering (or other technique) on first k egienvectors

    Inputs
        :mesh: <pymeshlab.Mesh> a mesh specifying the vertices and the faces
        :k: <int | None> clusters to seperate mesh into, if None then number is determined by finding the largest set of eigenvalues 
                         which are within ε away from each other, (default is None)
    
    Outputs
        :returns: <np.ndarray> Labels of size m x 1; m = len(mesh.vertex_matrix) where Labels[i] = label of vertex i ∈ [1, k]
    """
    # Step 1
    mesh_graph = FaceGraph(mesh, model_loc)

    # Step 2
    if(os.path.exists(f"{model_loc}/similarity_matrix.npy")):
        similarity_matrix = np.load(f"{model_loc}/similarity_matrix.npy")
    else:
        similarity_matrix = mesh_graph.similarity_matrix()

    # Step 3
    sqrt_degree = np.sqrt(mesh_graph.degree_matrix)
    laplacian = sqrt_degree.T * similarity_matrix.T * sqrt_degree

    # Step 4
    eigen_values, eigen_vectors = scipy.sparse.linalg.eigsh(laplacian) # Eigen values here can be used to get the value of k  = num < epsilon (0.5)
    eigen_vectors /= np.linalg.norm(eigen_vectors, axis=1)[:,None]

    # Step 5
    _, labels = kmeans2(eigen_vectors, k, minit="++", iter=50)
    vectors_labels = {}
    vectors_labels['vectors'] = eigen_vectors
    vectors_labels['values'] = eigen_values
    vectors_labels['labels']  = labels
    np.savez(f"{model_loc}/vectors_labels.npz",vectors_labels )
    print(f"Written labels and vectors to:{model_loc}/vectors_labels.npz")
    return labels
