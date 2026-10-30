import fitz

def extract_text_from_pdf(file_path: str):

    doc = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(doc):

        text = page.get_text()

        pages.append({
            "page": page_number + 1,
            "text": text
        })

    doc.close()

    return pages