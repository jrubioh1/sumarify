import os
import charset_normalizer
import PyPDF2
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
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
    print(os.environ["PATH"])
    def process_pdf_with_tesseract(file_data):
        file_info = {
            'file_format': 'pdf',
            'is_encrypted': False,
            'content': None,
            'is_normalized': False
        }

        try:
            # Convertimos el PDF en imágenes por página
            images = convert_from_bytes(file_data)
            content = ""
            for image in images:
                # Aplicamos Tesseract OCR a cada imagen
                text = pytesseract.image_to_string(image, lang='eng')  # Cambiar 'eng' por el idioma necesario
                content += text + "\n"
            file_info['content'] = content.strip()
            file_info['is_normalized'] = bool(content.strip())
        except Exception as e:
            file_info['content'] = f"Error processing PDF with Tesseract: {str(e)}"

        return file_info

    def process_image_with_tesseract(file_data):
        file_info = {
            'file_format': 'image',
            'content': None,
            'is_normalized': False
        }

        try:
            # Convertimos la imagen a texto con Tesseract
            image = Image.open(BytesIO(file_data))
            text = pytesseract.image_to_string(image, lang='eng')  # Cambiar 'eng' por el idioma necesario
            file_info['content'] = text.strip()
            file_info['is_normalized'] = bool(text.strip())
        except Exception as e:
            file_info['content'] = f"Error processing image with Tesseract: {str(e)}"

        return file_info

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