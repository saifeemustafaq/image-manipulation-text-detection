import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import sys
import os
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfReader
from PIL import ImageDraw
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal

# Your new function for creating a PDF from images
def create_pdf_from_images(images, pdf_path):
    """
    Create a single PDF file from a list of images.
    Args:
    - images: A list of PIL Image objects.
    - pdf_path: The path where the PDF should be saved.
    """
    # Ensure images are in RGB mode for PDF conversion
    rgb_images = [img.convert('RGB') for img in images]
    # Save all the images as a single PDF file
    rgb_images[0].save(pdf_path, save_all=True, append_images=rgb_images[1:])

class Worker(QThread):
    progress_signal = pyqtSignal(int)  # Signal to update progress
    
    def __init__(self, source_folder, output_folder, x_image_path):
        super(Worker, self).__init__()
        self.source_folder = source_folder
        self.output_folder = output_folder
        self.x_image_path = x_image_path
        
    def run(self):
        process_folder(self.source_folder, self.output_folder, self.x_image_path, self.update_progress)

    def update_progress(self, value):
        self.progress_signal.emit(value)

# Your previous functions (process_folder, convert_pdf_to_square, etc.) should be here

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



def convert_pdf_to_square(pdf_path, output_folder, x_image_path, progress_callback=None):

    images = convert_from_path(pdf_path)
    x_image = Image.open(x_image_path)
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
        new_image = add_borders(new_image, "black", 40, 40)

        # Add the x_image
        # Calculate the horizontal center position
        x_image_x_position = (new_image.width - x_image.width) // 2

        # Check if the Ximage has a transparency layer (alpha channel)
        if x_image.mode == 'RGBA':
            # Use the alpha channel as the mask
            new_image.paste(x_image, (x_image_x_position, 40), mask=x_image.split()[3])
        else:
            new_image.paste(x_image, (x_image_x_position, 40))

        squared_images.append(new_image)

        if progress_callback:  # Renamed to more accurately reflect it's a callback function now
            progress_callback(1)




        # Update progress bar for each page processed
        # pbar.update(1)

    
    base_file_name = os.path.basename(pdf_path)
    file_name_without_extension = os.path.splitext(base_file_name)[0]
    img_directory = os.path.join(output_folder, file_name_without_extension)

    if not os.path.exists(img_directory):
        os.makedirs(img_directory)

    for idx, new_image in enumerate(squared_images):
        new_image.save(os.path.join(img_directory, f'page_{idx + 1}.png'))

    # After all images are processed and saved, create a PDF from these images
    pdf_output_path = os.path.join(img_directory, f'{file_name_without_extension}.pdf')
    create_pdf_from_images(squared_images, pdf_output_path)

def process_folder(source_folder, output_folder, x_image_path, progress_update_callback):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_files = [f for f in os.listdir(source_folder) if f.endswith(".pdf")]

    for file_name in pdf_files:
        pdf_path = os.path.join(source_folder, file_name)
        # Pass output_folder instead of the undefined output_path
        convert_pdf_to_square(pdf_path, output_folder, x_image_path, progress_update_callback)



class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_progress = 0

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Button to select source folder
        self.btn_source_folder = QPushButton('Select Source Folder', self)
        self.btn_source_folder.clicked.connect(self.select_source_folder)
        layout.addWidget(self.btn_source_folder)

        self.lbl_source_folder = QLabel('Source Folder: Not Selected', self)
        layout.addWidget(self.lbl_source_folder)

        # Button to select output folder
        self.btn_output_folder = QPushButton('Select Output Folder', self)
        self.btn_output_folder.clicked.connect(self.select_output_folder)
        layout.addWidget(self.btn_output_folder)

        self.lbl_output_folder = QLabel('Output Folder: Not Selected', self)
        layout.addWidget(self.lbl_output_folder)

        # Button to select Ximage
        self.btn_ximage_path = QPushButton('Select Ximage', self)
        self.btn_ximage_path.clicked.connect(self.select_ximage_path)
        layout.addWidget(self.btn_ximage_path)

        self.lbl_ximage_path = QLabel('Ximage: Not Selected', self)
        layout.addWidget(self.lbl_ximage_path)

        # Button to start the process
        self.btn_start = QPushButton('Start Process', self)
        self.btn_start.clicked.connect(self.start_process)
        layout.addWidget(self.btn_start)

        

        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.setWindowTitle('PDF Processor')
        self.setGeometry(300, 300, 300, 200)

    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            self.lbl_source_folder.setText(f"Source Folder: {folder}")
            self.SOURCE_FOLDER = folder

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.lbl_output_folder.setText(f"Output Folder: {folder}")
            self.OUTPUT_FOLDER = folder

    def select_ximage_path(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Ximage", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.lbl_ximage_path.setText(f"Ximage: {file_path}")
            self.XIMAGE_PATH = file_path

    def start_process(self):
        if hasattr(self, 'SOURCE_FOLDER') and hasattr(self, 'OUTPUT_FOLDER') and hasattr(self, 'XIMAGE_PATH'):
            
            # Calculate total pages across all PDFs for the progress bar
            pdf_files = [f for f in os.listdir(self.SOURCE_FOLDER) if f.endswith(".pdf")]
            total_pages = sum([len(PdfReader(os.path.join(self.SOURCE_FOLDER, pdf_file)).pages) for pdf_file in pdf_files])
            
            # Set the maximum value for the progress bar
            self.progress_bar.setMaximum(total_pages)

            # Start the processing
            self.worker = Worker(self.SOURCE_FOLDER, self.OUTPUT_FOLDER, self.XIMAGE_PATH)
            self.worker.progress_signal.connect(self.update_progress)
            self.worker.start()  # This starts the thread
            
        else:
            # Display some error message if paths aren't selected
            error_msg = QLabel('Please ensure all paths are selected!', self)
            error_msg.setAlignment(Qt.AlignCenter)
            error_msg.setStyleSheet("color: red;")
            self.layout().addWidget(error_msg)
    
    def update_progress(self, increment_value): # This function will be called every time a signal is emitted
        self.current_progress += increment_value
        self.progress_bar.setValue(self.current_progress)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
