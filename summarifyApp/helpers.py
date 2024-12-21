import charset_normalizer
import PyPDF2
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO


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
    
# Función para limpiar el árbol de directorios
def clean_directory_tree(tree):
    def clean(node):
        if isinstance(node, dict):
            return {
                key: clean(value)
                for key, value in node.items()
                if not key.startswith("__MACOSX") and not key.startswith("._")
            }
        elif isinstance(node, list):
            return [item for item in node if not item.startswith("._")]
        return node

    return clean(tree)

