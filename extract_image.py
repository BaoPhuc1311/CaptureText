import easyocr

def extract_text_from_image(image_path):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path)
    extracted_text = ' '.join([text[1] for text in result])
    return extracted_text

if __name__ == "__main__":
    image_path = "path_to_your_image.png"
    extracted_text = extract_text_from_image(image_path)
    print("Extracted Text:")
    print(extracted_text)
