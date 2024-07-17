import streamlit as st
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import fitz  # PyMuPDF
from PIL import Image
import tempfile
import io

def merge_pdfs(file_paths, convert_bw=False):
    if not file_paths:
        st.warning("Please select at least one PDF file.")
        return

    save_path = st.text_input("Save Merged PDF As:", "merged.pdf")
    if not save_path:
        return

    merger = PdfMerger()
    for pdf in file_paths:
        merger.append(pdf)

    with open(save_path, "wb") as f_out:
        merger.write(f_out)

    if convert_bw:
        convert_pdf_to_bw(save_path)

    st.success("PDF files merged successfully.")

def convert_pdf_to_bw(file_path):
    # Open the PDF file
    doc = fitz.open(file_path)
    bw_save_path = file_path.replace(".pdf", "_bw.pdf")
    writer = PdfWriter()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        bw_img = img.convert("L")

        # Save the black and white image as a temporary PNG file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img_file:
            bw_img.save(temp_img_file.name)
            temp_img_file_path = temp_img_file.name

        # Create a new PDF page with the black and white image
        img_reader = fitz.open(temp_img_file_path)
        img_pdf_bytes = img_reader.convert_to_pdf()
        img_page = PdfReader(io.BytesIO(img_pdf_bytes)).pages[0]
        writer.add_page(img_page)

    with open(bw_save_path, "wb") as output_pdf:
        writer.write(output_pdf)

def main():
    st.title("PDF Combiner")

    # File uploader
    uploaded_files = st.file_uploader("Select PDF Files", type=["pdf"], accept_multiple_files=True)
    if uploaded_files:
        file_paths = [f.name for f in uploaded_files]
        st.write("Selected files:", file_paths)

    # Checkbox for converting to black and white
    convert_to_bw = st.checkbox("Convert to Black and White")

    # Button to merge PDF files
    if st.button("Merge PDF Files"):
        merge_pdfs(uploaded_files, convert_bw=convert_to_bw)

    # Footer
    st.markdown("<div style='position: fixed; bottom: 0; width: 100%; text-align: center;'>by Vic Herrera</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()