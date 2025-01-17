import PyPDF2


def extract_pdf_text(pdf_path):
    '''
    Function used to extract raw text from a pdf
    '''
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text
