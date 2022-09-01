import pymeshlab
import numpy as np
from tqdm import tqdm

class MeshGraph():  
    """
    AF(vertices, faces) = A graph representing the mesh from the given vertices np.ndarray (n, 3) and faces np.ndarray (m, k)

    Representaiton Invariant:
        - mesh is manifold
    
    Representaiton Exposure:
        - access is granted to all attributes 
    """
    def __init__(self, vertices, faces):
        ### Represnetation ###
        self.vertices = vertices
        self.faces = faces

        self.adj_map = {i: [Vertex(vertices[i], i), set()] for i in range(vertices.shape[0])}
        self.populate_adj()
        self.construct()
        print(f"Constructed m{str(self)[1:]}")

    def populate_adj(self):
        """ Fills up the adjaceny map for this graph using the faces """
        for face in self.faces:
            for i, v in enumerate(face):
                self.adj_map[v][1] |= set(face)

    def construct(self):
        """ Constructs the graph using the Vertex object and returns an entry node """
        for i, [vertex, child_indices] in self.adj_map.items():
            for j in child_indices: 
                if j == i: continue
                vertex.add_child(self.adj_map[j][0])
        self.graph = self.adj_map[0][0]

        return self.graph
    
    def shortest_path(self, v1, v2):
        """
        Finds the shortest path between two vertices

        Inputs
            :v1: <Vertex> stating vertex, must be within the graph
            :v2: <Vertex> end vertex, must be within the graph 
        """
        if v1 == v2: return []
        #Todo: implement bfs

    def walk(self, v1, e = 0, limit = 1000):
        """
        Follows the different gradients emerging from vertex v1 and returns dict of vertices found along each gradient direction

        Inputs
            :v1: <Vertex> to follow gradients of
            :e: <float> how much change in gradient we allow
        
        Outputs
            :returns: <dict> mapping gradient -> list of vertices along that gradient
        """
        print(f"Beginning walk from {v1} with an epsilon of {e} with a limit of {limit} ...")
        return {v: v.follow_gradient(v1, e, {v1, v}, limit) for v in v1.children}

    def __str__(self) -> str:
        """ Override object.__str__ """
        edges = sum([len(data[1]) for data in self.adj_map.values()])
        return f"Mesh graph with {len(self.adj_map)} vertices and {edges / 2} edges"

class Vertex():
    """
    AF([x, y, z], i) = a vertex located at x, y, z with a set of children and index i  

    Representaiton Invariant:
        - vertex can not point to itself
    
    Representaiton Exposure:
        - access is granted to all attributes 
    """
    def __init__(self, coords, i) -> None:
        self.i = i
        self.x, self.y, self.z = coords
        self.children = set()
    
    def add_child(self, child):
        """ Adds a child to the vertex's children """
        self.children.add(child)

    def follow_gradient(self, v0, e = 0.0, visited = set(), limit = 1000):
        """
        Finds v child of self such that gradient(v0, self) is within e of gradient(self, v)
        Then preforms this recursively until the gradient is no longer within e of previous gradient or we run out of vertices

        Inputs
            :v0: <Vertex> representing first parent of v1
            :e: <float> how much change in gradient we allow
            :visited: <set> of vertices we have visited before
        
        Outputs
            :returns: <list> of children along the gradient of v0 and self
        """
        gradient_v0 = self.gradient(v0)
        children_along_gradient = [self]
        if len(visited) >= limit: return children_along_gradient
        # if len(visited) % 200 == 0: print(f"We have checked the gradient of {len(visited)} vertices ...")

        for child in self.children:
            if child in visited: continue
            visited.add(child)
    
            gradient_child = self.gradient(child)
            if np.all((gradient_child - gradient_v0) < e):
                children_along_gradient += child.follow_gradient(self, e, visited)
        
        return children_along_gradient

    def gradient(self, v):
        """ Computes the gradient between self and Vertex v """
        return np.array([abs(v.x - self.x), abs(v.y - self.y), abs(v.z - self.z)])
    
    def __str__(self) -> str:
        """ Override object.__str__ """
        return f"vertex located at ({self.x}, {self.y} {self.z})"

def _save_obj(vertices, faces, output_path):
    """ Saves a mesh as obj """
    mesh_set = pymeshlab.MeshSet()
    mesh_set.add_mesh(pymeshlab.Mesh(vertices, faces))
    mesh_set.save_current_mesh(output_path)

def _extract_vertices_and_faces(mesh, vertex_list):
    """ Converts a list of Vertex objects into a (vertices np.ndarray, faces np.ndarray) """
    indicies = []
    vertices = []
    index_map = {}

    for i, vertex in enumerate(vertex_list):
        indicies.append(vertex.i)
        vertices.append([vertex.x, vertex.y, vertex.z])
        index_map[vertex.i] = i

    faces = []
    old_faces = mesh.face_matrix()
    for face in old_faces:
        v1, v2, v3 = face
        if v1 not in indicies or v2 not in indicies or v3 not in indicies: continue
        faces.append([index_map[v] for v in face])
    
    return vertices, faces