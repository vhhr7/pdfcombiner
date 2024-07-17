import streamlit as st
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import fitz  # PyMuPDF
from PIL import Image
import tempfile
import io
import os

def merge_pdfs(file_paths, convert_bw=False):
    if not file_paths:
        st.warning("Please select at least one PDF file.")
        return

    save_path = os.path.join(tempfile.gettempdir(), "merged.pdf")

    merger = PdfMerger()
    for pdf in file_paths:
        merger.append(pdf)

    with open(save_path, "wb") as f_out:
        merger.write(f_out)

    if convert_bw:
        convert_pdf_to_bw(save_path)

    with open(save_path, "rb") as f_out:
        st.download_button(label="Download Merged PDF", data=f_out, file_name="merged.pdf", mime="application/pdf")

    st.success("PDF files merged successfully.")

    # Delete the temporary file after download
    os.remove(save_path)

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

        # Clean up temporary image file
        os.remove(temp_img_file_path)

    with open(bw_save_path, "wb") as output_pdf:
        writer.write(output_pdf)

    return bw_save_path

def display_footer():
    footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: black;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #eaeaea;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .footer .logo {
        height: 60px; /* Increased size */
        margin-right: 20px;
    }
    .footer .separator {
        border-left: 2px solid #eaeaea;
        height: 120px;
        margin-right: 20px;
    }
    </style>
    <div class="footer">
        <img class="logo" src="http://vicherrera.net/wp-content/uploads/2023/05/VicHerrera_Logo.svg" alt="Vic Herrera Logo">
        <div class="separator"></div>
        <div>
            <p>Developed by Vic Herrera | <a href="https://vicherrera.net" target="_blank">Vic Herrera</a> | <a href="https://datawava.com" target="_blank">datawava</a></p>
            <p>© Version 1.2  - July, 2024</p>
        </div>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)

def main():
    st.title("PDF Combiner")

    # File uploader
    uploaded_files = st.file_uploader("Select PDF Files", type=["pdf"], accept_multiple_files=True)
    if uploaded_files:
        file_paths = []
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.read())
                file_paths.append(tmp_file.name)

        st.write("Selected files:", [os.path.basename(path) for path in file_paths])

    # Checkbox for converting to black and white
    convert_to_bw = st.checkbox("Convert to Black and White")

    # Button to merge PDF files
    if st.button("Merge PDF Files"):
        if uploaded_files:
            merge_pdfs(file_paths, convert_bw=convert_to_bw)

    # Display footer
    display_footer()

if __name__ == "__main__":
    main()