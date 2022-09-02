from importlib.util import module_for_loader
import scipy
import pymeshlab
import numpy as np
from tqdm import tqdm

### Global Constants ###
_coords = lambda vertices, indicies: np.array([vertices[i] for i in indicies])

class FaceGraph():
    """
    AF(mesh) = Converts mesh into a face graph, where 
                - each node is a face 
                - faces have edges between them iff they are adjacent 
                - weights of the edge between fi and fj = w(fi, fj) = δ * (geodisc(fi, fj)) / avg_geodisc + (1 - δ) * (ang_dist(fi, fj)) / avg_ang_dist
                    - ang_dist(fi, fj) = η * (1 - cos(α(fi, fj))); η = 1 for α >= 180 and η -> 0 for α < 180
                    - geodisc(fi, fj) = distance from center of fi to center of fj

    Representation Invariant:
        - true
    
    Representation Exposure:
        - access granted to all attributes
    """
    def __init__(self, mesh, model_loc) -> None:
        self.mesh = mesh
        self.faces = mesh.face_matrix()
        self.vertices = mesh.vertex_matrix()
        self.model_loc = model_loc

        mesh_set = pymeshlab.MeshSet()
        mesh_set.add_mesh(pymeshlab.Mesh(mesh.vertex_matrix(), mesh.face_matrix()))
        mesh_set.compute_normal_per_face()

        self.face_normals = mesh_set.current_mesh().face_normal_matrix()
        self.m = self.faces.shape[0]
        
        print("----- Computing face adj ... ------")
        self.edge_to_faces = {}
        for i in tqdm(range(self.m)):
            v1, v2, v3 = self.faces[i]
            edge_1 = Edge(v1, v2)
            edge_2 = Edge(v2, v3)
            edge_3 = Edge(v1, v3)

            for edge in (edge_1, edge_2, edge_3):
                try: self.edge_to_faces[edge].append(i)
                except: self.edge_to_faces[edge] = [i]

        print("------ Computing avg_geodisc and avg_ang_dist ... ------")
        n = 0
        self.geodisc = np.zeros((self.m, self.m))
        self.ang_dist = np.zeros((self.m, self.m))
        for edge, [i, j] in tqdm(self.edge_to_faces.items()):
            ang_dist = self.__ang_dist(i, j)
            geodisc = self.__geodisc(_coords(self.vertices, self.faces[i]), _coords(self.vertices, self.faces[j]), edge)

            self.geodisc[i, j] = geodisc
            self.geodisc[j, i] = geodisc
            self.ang_dist[i, j] = ang_dist
            self.ang_dist[j, i] = ang_dist
            n += 2

        self.avg_geodisc = self.geodisc.sum() / n
        self.avg_ang_dist = self.ang_dist.sum() / n

        print(f"[avg_geodisc] >> {self.avg_geodisc}")
        print(f"[avg_ang_dist] >> {self.avg_ang_dist}")

        self.__construct_adj_matrix()

        self.degree_matrix = np.zeros((self.m, self.m))
        self.__construct_degree_matrix()
    
    def similarity_matrix(self):
        """
        Computes the similairty matrix of the graph
        """
        print("------ Computing similarity matrix ... ------")
        matrix = scipy.sparse.csgraph.dijkstra(self.adj_matrix)
        # matrix[matrix == np.nan] = 0
        inf_indices = np.where(np.isinf(matrix))
        matrix[inf_indices] = 0
        
        sigma = matrix.mean()
        print(f"[sigma] >> {sigma}")
        np.exp(-matrix / (2 * (sigma ** 2)))
        np.fill_diagonal(matrix, 1)
        np.save(f"{self.model_loc}/similarity_matrix.npy", matrix)
        return matrix

    ### Helper Methods ###
    def __construct_adj_matrix(self):
        """ Construct the m x m adjacency matrix """
        print("------ Computing face graph adjacency matrix ... ------")
        self.adj_matrix = self.__weights(delta = 0.03)

    def __weights(self, delta = 0.03):
        """ Compute the weights matrix where weight of face_1 --- face_2 = δ * (geodisc(fi, fj)) / avg_geodisc + (1 - δ) * (ang_dist(fi, fj)) / avg_ang_dist"""
        return delta * self.geodisc / self.avg_geodisc + (1 - delta) * self.ang_dist / self.avg_ang_dist

    def __geodisc(self, face_1, face_2, edge):
        """ Computes the geodistance between the centers of face_1 and face_2 over the edge"""
        edge_center = edge.mean(self.vertices)
        return np.linalg.norm(edge_center - face_1.mean(0)) + np.linalg.norm(edge_center - face_2.mean(0))
    
    def __ang_dist(self, i, j, eta = 0.15):
        """ Computes the angular distance between face_1 and face_2 = η * (1 - cos(α(fi, fj))); η = 1 for α >= 180 and η -> 0 for α < 180"""
        face_1 = self.faces[i]
        face_2 = self.faces[j]
        face_1_normal = self.face_normals[i]
        face_2_normal = self.face_normals[j]
        
        cos_alpha = np.dot(face_1_normal, face_2_normal) / np.linalg.norm(face_1_normal) / np.linalg.norm(face_2_normal)
        
        if not np.all(face_1_normal.dot(face_2.mean() - face_1.mean())) < 0: eta = 1
        return eta * (1 - cos_alpha)

    def __construct_degree_matrix(self):
        """ Construct the m x 1 degree matrix """
        self.degree_matrix = np.reciprocal(self.adj_matrix.sum(1))
    
### Helper Classes ###
class Edge():
    """ A simple edge where two edges are equal if they are euivalent sets """
    def __init__(self, v1, v2) -> None:
        self.v1 = v1
        self.v2 = v2
    
    def mean(self, vertices): 
        return (vertices[self.v1] + vertices[self.v2]) / 2

    def __iter__(self):
        for i in [self.v1, self.v2]: yield i
        
    def __eq__(self, __o: object) -> bool:
        return (self.v1 == __o.v1 and self.v2 == __o.v2) or (self.v1 == __o.v2 and self.v2 == __o.v1)
    
    def __hash__(self) -> int:
        return hash(self.v1) + hash(self.v2)

    def __str__(self) -> str:
        return f"{self.v1} ---- {self.v2}"

### Helper Functions ###
def _interesct(A, B) -> int:
    """ Determines if A ∩ B != Ø, 0 -> False, 1 -> True """
    for elm in A:
        if elm in B: return 1
    return 0