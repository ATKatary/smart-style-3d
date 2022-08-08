"""
imad views
"""
from .models import Mesh
from rest_framework import status
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .imad_utils.view_helpers import _is_subset

@api_view(['GET'])
def fetch(request, *args, **kwargs):
    """
    Fetches model with given id

    Inputs
       :param request: <HttpRequest> containing all relevant information for the event to be fetched
    
    Output
       :returns: Status ... 
                        ... HTTP_200_OK if the model is fetched successfully
                        ... HTTP_404_NOT_FOUND if no such model exists
                        ... HTTP_403_FORIBIDDEN if the model couldn’t be fetched
    """
    data = []
    request = request.GET
    fetch_fields = ["modelId"]
    event_status   = _is_subset(fetch_fields, request.keys())
    
    if event_status == status.HTTP_200_OK:
        model_id = request['modelId']
        
        mesh = Mesh.objects.get(id=model_id)
        
        if mesh: data['meshPath'] = mesh.path
        else: event_status = status.HTTP_404_NOT_FOUND
    
    return Response(status = event_status, data = data)