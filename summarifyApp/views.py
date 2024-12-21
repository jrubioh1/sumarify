import os
import zipfile
import tempfile
from rest_framework.decorators import api_view
from rest_framework.response import Response
from request_casting import request_casting
from summarifyApp.helpers import process_pdf_with_tesseract, process_image_with_tesseract, clean_directory_tree



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



# Vista de Django para procesar el ZIP y devolver un árbol limpio
@api_view(['POST'])
def directory_tree_from_zip(request):
    uploaded_file = request.data.get('file', None)
    if not uploaded_file:
        return Response({'error': 'The ZIP file has not been specified.'}, status=400)

    if not uploaded_file.name.lower().endswith('.zip'):
        return Response({'error': 'The provided file is not a ZIP archive.'}, status=400)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, uploaded_file.name)
            with open(zip_path, 'wb') as f:
                f.write(uploaded_file.read())

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                valid_files = [
                    file for file in zip_ref.namelist()
                    if not file.startswith("__MACOSX") and not file.startswith("._")
                ]
                zip_ref.extractall(temp_dir, members=valid_files)

            tree = {}
            for root, dirs, files in os.walk(temp_dir):
                current_level = tree
                for part in root[len(temp_dir):].strip(os.sep).split(os.sep):
                    if part:
                        current_level = current_level.setdefault(part, {})
                for dir_name in dirs:
                    current_level[dir_name] = {}
                filtered_files = [file for file in files if file != uploaded_file.name]
                if filtered_files:
                    current_level['files'] = [file.encode('utf-8').decode('utf-8') for file in filtered_files]

            cleaned_tree = clean_directory_tree(tree)

            return Response({
                'message': 'The process was successful.',
                'zip_file': uploaded_file.name,
                'result': cleaned_tree
            }, status=200)

    except Exception as e:
        return Response({'error': f"Error processing the ZIP file: {str(e)}"}, status=500)
    
@api_view(['POST'])
def get_file_content(request):

    uploaded_file = request.data.get('file', None)
    if not uploaded_file:
        return Response({'error': 'The file has not been specified.'}, status=400)

    try:
        raw_data = uploaded_file.read()
        file_name = uploaded_file.name
        file_info = {}

        if file_name.endswith('.pdf'):
            file_info = process_pdf_with_tesseract(raw_data)
        elif file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            file_info = process_image_with_tesseract(raw_data)
        else:
            file_info['content'] = "Unsupported file type. Please upload a PDF or an image file."
            file_info['file_format'] = "unknown"
            file_info['is_normalized'] = False

        # Añadimos el nombre del archivo al resultado
        file_info['file_name'] = file_name
        return Response(file_info, status=200)

    except Exception as e:
        return Response({'error': f"Error processing the file: {str(e)}"}, status=500)