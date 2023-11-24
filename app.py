import tempfile
from langchain.document_loaders import UnstructuredPDFLoader
import streamlit as st
import streamlit_scrollable_textbox as stx
import fitz
import pdfplumber
from io import BytesIO
import requests




class RapidOCRTextExtractor:
    def __init__(self, pdf_url):
        self.pdf_url = pdf_url

    def extract_text(self):
        # Download the PDF from the URL
        response = requests.get(self.pdf_url)
        pdf_bytes = response.content

        # Initialize the RapidOCR OCR engine
        ocr = OCR()

        # Extract text from the PDF
        result = ocr.run(BytesIO(pdf_bytes))

        # Combine the text from the result
        text_content = [line['text'] for page_result in result for line in page_result]

        return text_content



class UnstructuredPDFReader:
    def __init__(self, pdf_bytes, extract_images=True, mode="elements"):
        self.pdf_bytes = pdf_bytes
        self.extract_images = extract_images
        self.mode = mode

    def extract_text(self):
        # Save the bytes to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(self.pdf_bytes)
            file_path = tmp.name

            loader = UnstructuredPDFLoader(file_path, extract_images=self.extract_images, mode=self.mode)
            data = loader.load()

            # Extract 'page_content' values and return them
            text_content = [document.page_content for document in data if not isinstance(document, str) and hasattr(document, 'page_content')]

        return text_content



class PDFPlumberTextExtractor:
    def __init__(self, pdf_bytes):
        self.pdf_bytes = pdf_bytes

    def extract_text(self):
        pdf_file = BytesIO(self.pdf_bytes)
        pdf = pdfplumber.open(pdf_file)
        text_content = []

        for page in pdf.pages:
            text = page.extract_text()
            text_content.append(text)

        return text_content


class PyMuPDFTextExtractor:
    def __init__(self, pdf_bytes):
        self.pdf_bytes = pdf_bytes

    def extract_text(self):
        doc = fitz.open(stream=self.pdf_bytes, filetype="pdf")
        text_content = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            text_content.append(text)

        return text_content


def main():
    st.set_page_config(layout="wide")

    st.title("PDF Text Extraction")

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file is not None:
        pdf_bytes = uploaded_file.read()

        extraction_method = st.radio(
            "Select Text Extraction Method",
            ["Unstructured PDFLoader", "PDFPlumber", "PyMuPDF", "RapidOCR"]  # Add "RapidOCR" as an option
        )

        if extraction_method == "Unstructured PDFLoader":
            pdf_reader = UnstructuredPDFReader(pdf_bytes)
        elif extraction_method == "PDFPlumber":
            pdf_reader = PDFPlumberTextExtractor(pdf_bytes)
        elif extraction_method == "PyMuPDF":
            pdf_reader = PyMuPDFTextExtractor(pdf_bytes)
        elif extraction_method == "RapidOCR":  # Add handling for RapidOCR
            pdf_url = "https://arxiv.org/pdf/2103.15348.pdf"  # Replace with your PDF URL
            pdf_reader = RapidOCRTextExtractor(pdf_url)

        extracted_text = pdf_reader.extract_text()

        col1, col2 = st.columns(2)

        with col1:
            st.header("Text Extraction Options")
            extraction_option = st.radio("Select Text Extraction Option", ["Entire Text", "Specific Parts"])

        with col2:
            if extraction_option == "Specific Parts":
                st.header("Specify a prefix to extract specific parts")
                prefix = st.text_input("Enter a Prefix (e.g., LV)")

        if extraction_option == "Entire Text":
            st.header("Entire Extracted Text")
            max_chars = 5000
            entire_text = "\n".join(extracted_text)
            stx.scrollableTextbox(entire_text, height=400, border=True)
        elif extraction_option == "Specific Parts":
            if prefix:
                st.header(f"Extracted Text Matching the Prefix '{prefix}'")
                matching_text = [line for page_text in extracted_text for line in page_text.split('\n') if line.startswith(prefix)]
                if matching_text:
                    for match in matching_text:
                        st.write(match)
                else:
                    st.write(f"No text found starting with the prefix '{prefix}'.")
            else:
                st.warning("Please enter a prefix to extract text.")

if __name__ == "__main__":
    main()


