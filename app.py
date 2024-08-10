from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import pdfplumber
import io
import streamlit_pills as sp

# Configure API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Load gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

def get_gemini_response(input, image, prompt):
    response = model.generate_content([input, image[0], prompt])
    return response.text

def input_image_setup(uploaded_img):
    if uploaded_img is not None:
        bytes_data = uploaded_img.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_img.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("Image not found")

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def input_file_setup(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.type.startswith('image'):
            bytes_data = uploaded_file.getvalue()
            image_parts = [
                {
                    "mime_type": uploaded_file.type,
                    "data": bytes_data
                }
            ]
            return image_parts
        elif uploaded_file.type.startswith('application/pdf'):
            text = extract_text_from_pdf(uploaded_file)
            return [{"text": text}]
        else:
            raise ValueError("Unsupported file type")
    else:
        raise FileNotFoundError("File not found")

st.set_page_config(page_title="Invoice Information Extractor", page_icon="🔮")
st.title("Invoice Information Extractor 📃")

st.write("Upload your invoice (image or PDF)")

# Display sample prompts

uploaded_file = st.file_uploader("Upload an Invoice Image 🖼️ or PDF 📄", type=["jpg", "jpeg", "png", "pdf"])

selected = sp.pills(" Ask a question related to the invoice. Here are some example prompts:", 
                        ["What is the total amount?",
                         'What are the Customter details?' , 
                         'What is the information about the Products?'],
                        clearable=True,index=None)

# input_query = st.text_input("Ask a question about the invoice", key="input")
input_query = selected if selected else st.text_input("Ask a question about the invoice", key="input")

if uploaded_file is not None:
    if uploaded_file.type.startswith('image'):
        image = Image.open(uploaded_file)
        st.image(image, caption="Image uploaded.", use_column_width=True)
    elif uploaded_file.type.startswith('application/pdf'):
        st.write("PDF uploaded.")

submit = st.button("Submit")

input_prompt = """
You are an expert in understanding invoices. We will show you an invoice and you have to answer the following questions based on the invoice:
"""

if submit:
    file_data = input_file_setup(uploaded_file)
    response = get_gemini_response(input_prompt, file_data, input_query)
    st.subheader("Response🤖:")
    st.write(response)
