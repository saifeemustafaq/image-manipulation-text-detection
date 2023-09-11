import sys
import os
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfFileWriter, PdfFileReader

def convert_pdf_to_square(pdf_path, output_path):
    images = convert_from_path(pdf_path)
    squared_images = []

    for img in images:
        width, height = img.size
        new_width = height  # Making the width equal to the height
        delta = new_width - width
        left_padding = delta // 2
        right_padding = delta - left_padding

        new_image = Image.new('RGB', (new_width, height), color='white')
        new_image.paste(img, (left_padding, 0))
        squared_images.append(new_image)

    # Saving squared images back to PDF
    squared_images[0].save(output_path, save_all=True, append_images=squared_images[1:])

def process_folder(source_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(source_folder):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(source_folder, file_name)
            output_path = os.path.join(output_folder, file_name)
            convert_pdf_to_square(pdf_path, output_path)
            print(f"Processed {file_name} to {output_path}")

if __name__ == "__main__":
    SOURCE_FOLDER = r"C:\Users\Mustafa\Desktop\SLH\Test"
    OUTPUT_FOLDER = r"C:\Users\Mustafa\Desktop\SLH\Test"
    process_folder(SOURCE_FOLDER, OUTPUT_FOLDER)
