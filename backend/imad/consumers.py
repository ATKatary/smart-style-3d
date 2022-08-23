import os
import json
from .models import Mesh
from .imad_utils.view_helpers import report
from channels.generic.websocket import WebsocketConsumer

### Global Constants ###

class MeshConsumer(WebsocketConsumer):
    """
    AF(interpreter, interpreter_path, container_name) = a consumer for executing scripts inside a container session

    Representation Invariant
      - inherits from WebsocketConsumer
   
    Representation Exposure
      - inherits from WebsocketConsumer
      - access allowed to all fields but they are all immutable
    """
    def connect(self): 
        """
        Connects to the interperter and creates a script inside the container with the id defined when the socket connection was made
        """
        print("Connecting ....")
        self.mesh = Mesh()
        self.accept()

    def disconnect(self, close_code): 
        """
        Disoconnects from the interperter and deletes the script 
        """
        try: 
            print("Closing ....")
            # os.remove(self.mesh.path)
            
        except Exception as error: print(f"Error occurred while removing script {self.mesh.path}:\n{report(error)}")

    def receive(self, text_data = None):
        """
        Creates a temperorary Mesh for use to experiment with

        Inputs 
            :param text_data: <json> string containing the info for the mesh to upload
        """
        text_data = json.loads(text_data)
        print("Mesh Recieved ....")
        
        response = {}
        data = text_data['data']
        type_ = text_data['type']
        try:
            if type_ == "upload": self.mesh.overwrite(data)
            elif type_ == "text2mesh":
                self.mesh.text2mesh(data)

            self.mesh.extract()
            head, tail = os.path.split(self.mesh.path)
            name, ext = os.path.splitext(tail)
            
            response = {
                'name': name,
                'ext': ext,
                'f': self.mesh.faces,
                'v': self.mesh.vertices,
                'vn': self.mesh.vertex_normals,
            }
            
        except Exception as error: print(f"Error happened while responding to a {type_} request:\n{report(error)}")

        self.send(text_data = json.dumps(response))
