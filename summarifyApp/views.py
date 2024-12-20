import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from request_casting import request_casting

# @api_view(['GET', 'POST'])
# def my_view(request):
#     if request.method == 'GET':
#         return Response({"message": "This is a GET request"})
#     elif request.method == 'POST':
#         return Response({"message": "This is a POST request"})


@api_view(['GET'])
def directory_tree(request):
    request.PATH= request_casting.RequestString(request, 'path', None)
    
    if request.PATH is None:
        return Response({'error': 'The path has not been specified.'}, 400)
    print(request.PATH)
    if not os.path.isdir(request.PATH):
        return Response({'error': 'The path must specify a directory.'}, 400)
    
    print(f'The chosen path for processing is the following:{request.PATH}')   
    tree = {}
    for root, dirs, files in os.walk(request.PATH):
        # Navegar y construir la estructura jerárquica del árbol
        current_level = tree
        # Divide el nivel actual usando la parte relativa del path
        for part in root[len(request.PATH):].strip(os.sep).split(os.sep):
            if part:
                current_level = current_level.setdefault(part, {})
        # Agrega subdirectorios
        for dir_name in dirs:
            current_level[dir_name] = {}
        # Agrega archivos 
        current_level['files'] = []
        for file_name in files:
            
            
             current_level['files'].append(file_name)
            

    return Response({'message':'The procces is success.', 'path':request.PATH ,'result': tree},200)