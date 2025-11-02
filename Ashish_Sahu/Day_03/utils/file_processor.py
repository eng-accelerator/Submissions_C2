import base64
import io
from PIL import Image
from typing import Dict, Any, List
import PyPDF2
import docx

def process_uploaded_file(uploaded_file) -> Dict[str, Any]:
    file_type = uploaded_file.type
    file_name = uploaded_file.name

    if file_type.startswith('image/'):
        return process_image(uploaded_file, file_name)
    elif file_type == 'application/pdf':
        return process_pdf(uploaded_file, file_name)
    elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return process_docx(uploaded_file, file_name)
    elif file_type.startswith('text/') or file_name.endswith(('.txt', '.md', '.csv', '.json', '.py', '.js', '.html', '.css')):
        return process_text(uploaded_file, file_name)
    else:
        return {
            'name': file_name,
            'type': 'unsupported',
            'content': None,
            'error': 'Unsupported file type'
        }

def process_image(uploaded_file, file_name: str) -> Dict[str, Any]:
    try:
        image = Image.open(uploaded_file)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return {
            'name': file_name,
            'type': 'image',
            'content': img_str,
            'format': 'base64',
            'mime_type': 'image/png'
        }
    except Exception as e:
        return {
            'name': file_name,
            'type': 'image',
            'content': None,
            'error': str(e)
        }

def process_pdf(uploaded_file, file_name: str) -> Dict[str, Any]:
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text_content = []

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content.append(page.extract_text())

        full_text = "\n\n".join(text_content)

        return {
            'name': file_name,
            'type': 'pdf',
            'content': full_text,
            'format': 'text',
            'pages': len(pdf_reader.pages)
        }
    except Exception as e:
        return {
            'name': file_name,
            'type': 'pdf',
            'content': None,
            'error': str(e)
        }

def process_docx(uploaded_file, file_name: str) -> Dict[str, Any]:
    try:
        doc = docx.Document(uploaded_file)
        text_content = []

        for paragraph in doc.paragraphs:
            text_content.append(paragraph.text)

        full_text = "\n".join(text_content)

        return {
            'name': file_name,
            'type': 'docx',
            'content': full_text,
            'format': 'text'
        }
    except Exception as e:
        return {
            'name': file_name,
            'type': 'docx',
            'content': None,
            'error': str(e)
        }

def process_text(uploaded_file, file_name: str) -> Dict[str, Any]:
    try:
        content = uploaded_file.read().decode('utf-8')

        return {
            'name': file_name,
            'type': 'text',
            'content': content,
            'format': 'text'
        }
    except Exception as e:
        return {
            'name': file_name,
            'type': 'text',
            'content': None,
            'error': str(e)
        }

def format_files_for_context(files: List[Dict[str, Any]]) -> str:
    context_parts = []

    for file in files:
        if file.get('error'):
            continue

        if file['format'] == 'text':
            context_parts.append(f"File: {file['name']}\n{file['content']}")

    return "\n\n---\n\n".join(context_parts) if context_parts else ""
