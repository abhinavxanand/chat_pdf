# PDF Chat Assistant

A Streamlit-based web application that allows users to chat with their PDF documents using Azure OpenAI's GPT models and RAG (Retrieval-Augmented Generation).

## Features

- PDF document processing and text extraction
- Semantic search using FAISS and Sentence Transformers
- Interactive chat interface with Azure OpenAI integration
- Context-aware responses based on PDF content

## Prerequisites

- Python 3.8 or higher
- Azure OpenAI API access
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone the repository
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root with your Azure OpenAI credentials:
```
AZURE_API_KEY=your_api_key
AZURE_API_BASE=your_endpoint
AZURE_API_VERSION=your_api_version
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided local URL (typically http://localhost:8501)

3. Enter your Azure OpenAI credentials in the sidebar (if not provided via .env)

4. Upload a PDF document

5. Start asking questions about the content of your PDF!

## How it Works

The application uses a RAG (Retrieval-Augmented Generation) approach:
1. PDF text is extracted and split into chunks
2. Chunks are embedded using Sentence Transformers
3. FAISS is used for efficient similarity search
4. Relevant context is retrieved and sent to Azure OpenAI
5. GPT model generates context-aware responses

## License

MIT License 