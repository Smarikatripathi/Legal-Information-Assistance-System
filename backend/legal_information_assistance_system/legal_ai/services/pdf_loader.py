import os

def load_pdf(file_name):
    path = os.path.join("media/pdfs", file_name)
    return path