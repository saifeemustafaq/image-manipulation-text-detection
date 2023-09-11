import sys
import os
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfReader
from tqdm import tqdm
from PIL import ImageDraw

from PIL import ImageDraw

def add_borders(img, border_color, border_size, corner_radius=0):
    """Add a border around the image with the specified color and size."""
    bordered_image = Image.new('RGB', 
                     (img.width + 2 * border_size, img.height + 2 * border_size), 
                     color=border_color)
    if corner_radius > 0:
        # Draw rounded rectangle
        mask = Image.new('L', img.size, 0)  # Adjusted the size here
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), (img.width, img.height)], corner_radius, fill=255)
        bordered_image.paste(img, (border_size, border_size), mask=mask)
    else:
        bordered_image.paste(img, (border_size, border_size))
    return bordered_image



def convert_pdf_to_square(pdf_path, output_path, pbar):
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
        
        # Add borders
        new_image = add_borders(new_image, "white", 4)
        new_image = add_borders(new_image, "black", 20, 20)

        
        squared_images.append(new_image)

        # Update progress bar for each page processed
        pbar.update(1)

    # Saving squared images back to PDF
    squared_images[0].save(output_path, save_all=True, append_images=squared_images[1:])


def process_folder(source_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_files = [f for f in os.listdir(source_folder) if f.endswith(".pdf")]

    # Calculate total pages across all PDFs
    # Calculate total pages across all PDFs
    total_pages = sum([len(PdfReader(os.path.join(source_folder, pdf_file)).pages) for pdf_file in pdf_files])


    with tqdm(total=total_pages, desc="Processing Pages", unit="page") as pbar:
        for file_name in pdf_files:
            pdf_path = os.path.join(source_folder, file_name)
            output_path = os.path.join(output_folder, file_name)
            convert_pdf_to_square(pdf_path, output_path, pbar)

if __name__ == "__main__":
    SOURCE_FOLDER = r"C:\Users\Mustafa\Desktop\SLH\Test"
    OUTPUT_FOLDER = r"C:\Users\Mustafa\Desktop\SLH\Test"
    process_folder(SOURCE_FOLDER, OUTPUT_FOLDER)
