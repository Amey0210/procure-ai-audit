import os
import io
import json
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import chromadb
from chromadb.utils import embedding_functions
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pypdf import PdfReader
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv  # Added

# Load environment variables from .env file
load_dotenv()  # Added

app = FastAPI()

# Enable CORS for SAP CAP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Config
# Securely fetch the key from environment
api_key = os.getenv("GROQ_API_KEY") 
if not api_key:
    raise ValueError("GROQ_API_KEY is not set in the environment or .env file")
    
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0, api_key=api_key)

# 2. VectorDB
client = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection(name="supplier_contracts", embedding_function=ef)

class PORequest(BaseModel):
    text: str

# Unified Analysis Function
def run_audit(contract_context, po_text):
    # Note: Double curly braces {{ }} escape the JSON structure for LangChain
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an SAP Auditor. Analyze the PO against the Contract.
        Return ONLY valid JSON in this format:
        {{
            "id": "PO-ID",
            "vendor": "Vendor Name",
            "amount": 0.0,
            "items": "Item details",
            "analysis": "Detailed audit report",
            "risk_score": 1.0
        }}"""),
        ("user", "Contract: {context}\n\nPO: {po}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"context": contract_context, "po": po_text})
    
    # Clean the response to ensure valid JSON
    content = response.content.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(content)
    except:
        # Fallback if AI fails to return perfect JSON
        return {
            "id": "ERROR", "vendor": "Unknown", "amount": 0.0, 
            "items": "Extraction failed", "analysis": response.content, "risk_score": 5.0
        }

@app.post("/analyze-po")
async def analyze_po(request: PORequest):
    results = collection.query(query_texts=[request.text], n_results=1)
    context = results['documents'][0][0]
    return run_audit(context, request.text)

@app.post("/analyze-pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    content = await file.read()
    pdf = PdfReader(io.BytesIO(content))
    extracted_text = "".join([page.extract_text() for page in pdf.pages])
    
    results = collection.query(query_texts=[extracted_text], n_results=1)
    context = results['documents'][0][0]
    
    return run_audit(context, extracted_text)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)