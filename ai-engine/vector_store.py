import chromadb
from chromadb.utils import embedding_functions

# Use a persistent path so data isn't lost when you restart
client = chromadb.PersistentClient(path="./chroma_db")

# This is the "Meaning-to-Number" function
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Create a collection for Supplier Contracts
collection = client.get_or_create_collection(name="supplier_contracts", embedding_function=ef)

def add_contract(supplier_id, text):
    collection.add(
        documents=[text],
        metadatas=[{"supplier_id": supplier_id}],
        ids=[supplier_id]
    )

def query_contracts(query_text):
    return collection.query(query_texts=[query_text], n_results=1)