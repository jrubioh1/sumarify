import os
import charset_normalizer
import PyPDF2
from io import BytesIO
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


@api_view(['POST'])
def get_file_content(request):
    def process_pdf(file_data):
        file_info = {
            'file_format': 'pdf',
            'is_encrypted': False,
            'content': None,
            'is_normalized': False
        }

        try:
            pdf_stream = BytesIO(file_data)
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            if pdf_reader.is_encrypted:
                file_info['is_encrypted'] = True
                file_info['content'] = "PDF is encrypted, unable to extract content."
            else:
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text()
                file_info['content'] = content.strip()
                file_info['is_normalized'] = bool(content.strip())
        except Exception as e:
            file_info['content'] = f"Error processing PDF: {str(e)}"

        return file_info

    def process_text_file(file_data):
        file_info = {
            'file_format': 'text',
            'is_encrypted': False,
            'content': None,
            'is_normalized': False
        }

        try:
            result = charset_normalizer.detect(file_data)
            encoding = result['encoding']
            if encoding:
                file_info['content'] = file_data.decode(encoding, errors='replace')
                file_info['is_normalized'] = True
            else:
                file_info['content'] = "Unable to detect encoding or non-text content."
        except Exception as e:
            file_info['content'] = f"Error processing text file: {str(e)}"

        return file_info

    uploaded_file = request.data.get('file', None)
    if not uploaded_file:
        return Response({'error': 'The file has not been specified.'}, status=400)

    try:
        raw_data = uploaded_file.read()
        file_name = uploaded_file.name
        file_info = {}

        if file_name.endswith('.pdf'):
            file_info = process_pdf(raw_data)
        else:
            file_info = process_text_file(raw_data)

        # Añadir el nombre del archivo al resultado
        file_info['file_name'] = file_name
        return Response(file_info, status=200)

    except Exception as e:
        return Response({'error': f"Error processing the file: {str(e)}"}, status=500)