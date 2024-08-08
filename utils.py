import PyPDF2
import docx

def process_pdf(file):
    reader = PyPDF2.PdfFileReader(file)
    content = ""
    for page_num in range(reader.numPages):
        page = reader.getPage(page_num)
        content += page.extractText()
    return content

def process_docx(file):
    doc = docx.Document(file)
    content = ""
    for paragraph in doc.paragraphs:
        content += paragraph.text + "\n"
    return content

def process_txt(file):
    return file.read().decode("utf-8")

def process_document(file):
    if file.type == "application/pdf":
        return process_pdf(file)
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return process_docx(file)
    elif file.type == "text/plain":
        return process_txt(file)
    else:
        raise ValueError("Unsupported file type")
