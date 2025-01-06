import PyPDF2
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Tuple
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class PDFChatEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.chunk_size = 200
        self.overlap = 50
        self.chunks = []
        self.faiss_index = None
        
    def process_pdf(self, pdf_file) -> str:
        """Process PDF file and create searchable index"""
        text = self._extract_text(pdf_file)
        chunks = self._chunk_text(text)
        embeddings = self._create_embeddings(chunks)
        self._build_index(embeddings)
        return text
    def _extract_text(self, pdf_file) -> str:
        """Extract text from PDF file"""
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
        
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk = " ".join(words[i:i + self.chunk_size])
            chunks.append(chunk)
        self.chunks = chunks
        return chunks
        
    def _create_embeddings(self, chunks: List[str]) -> np.ndarray:
        """Create embeddings for chunks"""
        return self.model.encode(chunks)
        
    def _build_index(self, embeddings: np.ndarray):
        """Build FAISS index"""
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        self.faiss_index = index
        
    def get_answer(self, question: str, api_key: str, azure_endpoint: str, api_version: str) -> str:
        """Get answer for question using RAG"""
        if not self.faiss_index:
            return "Please upload a PDF first."
            
        # Get relevant chunks
        question_embedding = self.model.encode([question])
        D, I = self.faiss_index.search(question_embedding.astype('float32'), k=3)
        context = " ".join([self.chunks[i] for i in I[0]])
        
        # Generate answer using Azure OpenAI
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version
        )
        
        prompt = f"""Based on the following context, please answer the question.
        Context: {context}
        Question: {question}
        Answer:"""
        
        response = client.chat.completions.create(
            model="ak-gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content