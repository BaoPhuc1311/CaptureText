import fitz

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        extracted_text += page.get_text()
    
    return extracted_text

if __name__ == "__main__":
    pdf_path = "path_to_your_pdf.pdf"
    extracted_text = extract_text_from_pdf(pdf_path)
    print("Extracted Text:")
    print(extracted_text)
