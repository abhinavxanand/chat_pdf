import streamlit as st
from utils import PDFChatEngine
import os
from dotenv import load_dotenv
import base64


load_dotenv()

def display_pdf(pdf_path):
    """Display PDF in Streamlit"""
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'engine' not in st.session_state:
        st.session_state.engine = PDFChatEngine()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'pdf_processed' not in st.session_state:
        st.session_state.pdf_processed = False
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""

def main():
    st.set_page_config(page_title="Chat with PDF", page_icon="📚", layout="wide")
    initialize_session_state()

    st.title("PDF Chat Assistant")
    
    # Sidebar for Azure OpenAI credentials
    with st.sidebar:
        api_key = st.text_input("Azure OpenAI API Key", value=os.getenv('AZURE_API_KEY', ''), type='password')
        azure_endpoint = st.text_input("Azure OpenAI Endpoint", value=os.getenv('AZURE_API_BASE', ''), type='password')
        api_version = st.text_input("Azure OpenAI API Version", value=os.getenv('AZURE_API_VERSION', ''))
        st.markdown("""
        ### Instructions:
        1. Enter your Azure OpenAI credentials
        2. Upload a PDF file
        3. Ask questions about the content
        """)
    
    col1, col2 = st.columns([1, 1])

    with col1:
        # File upload
        uploaded_file = st.file_uploader("Upload your PDF", type=['pdf'])
        
        if uploaded_file and not st.session_state.pdf_processed:
            with st.spinner('Processing PDF...'):
            # Process PDF and get extracted text
                extracted_text = st.session_state.engine.process_pdf(uploaded_file)
                st.session_state.pdf_processed = True
                st.session_state.extracted_text = extracted_text
                st.success('PDF processed successfully!')
        
        if st.session_state.get('pdf_processed', False):
            with st.expander("View PDF Content", expanded=False):
                st.markdown("### PDF Content")
                st.markdown(
                    f'''
                    <div style="height: 400px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; background-color: white;">
                        <pre style="white-space: pre-wrap;">{st.session_state.extracted_text}</pre>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
        # Chat interface
        st.markdown("### Chat")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Query input
        if question := st.chat_input("Ask a question about your PDF"):
            if not api_key or not azure_endpoint or not api_version:
                st.error("Please enter all Azure OpenAI credentials in the sidebar.")
                return
                
            if not st.session_state.pdf_processed:
                st.error("Please upload a PDF first!")
                return
                
            # Add user message
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            
            # Get and display assistant response
            with st.chat_message("assistant"):
                with st.spinner('Thinking...'):
                    response = st.session_state.engine.get_answer(question, api_key, azure_endpoint, api_version)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

        with col2:
            # PDF viewer section
            # st.markdown("### PDF View")
            if st.session_state.pdf_processed and st.session_state.engine.pdf_path:
                display_pdf(st.session_state.engine.pdf_path)

if __name__ == "__main__":
    main()
