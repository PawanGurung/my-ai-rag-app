import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
from google import genai
import chromadb
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Add CORS middleware to accept local frontend development traffic
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins to securely test locally
    allow_credentials=True,
    allow_methods=["*"],  # Opens up POST and GET request pathways
    allow_headers=["*"],
)

# 1. Initialize Google Gemini Client
gemini_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_key)

# 2. Initialize Local ChromaDB Client (Saves data inside a local folder)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create an AI storage pool (Collection) inside ChromaDB for our documents
collection = chroma_client.get_or_create_collection(name="company_knowledge")

# 3. Automation Script: Read the text file and load it into ChromaDB
def ingest_documents():
    file_path = "./documents/company_policy.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            text_content = f.read()
        
        # Split the text document by newlines into distinct lines
        text_chunks = [line.strip() for line in text_content.split("\n") if line.strip()]
        
        # Create unique IDs for database tracking
        chunk_ids = [f"id_{i}" for i in range(len(text_chunks))]
        
        # Add the documents straight into ChromaDB (It handles embeddings automatically!)
        collection.upsert(
            documents=text_chunks,
            ids=chunk_ids
        )
        print("🎉 SUCCESS: Documents successfully indexed into ChromaDB!")

# Trigger our data ingestion script when the application boots up
ingest_documents()

class ChatRequest(BaseModel):
    message: str

@app.post("/api/v1/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # Step A: Query ChromaDB for the closest matching reference text fragment
        db_results = collection.query(
            query_texts=[request.message],
            n_results=1  # Bring back only the single best matching sentence
        )
        
        # Extract the matched text chunk from the database output array
        retrieved_context = db_results['documents'][0] if db_results['documents'] else ["No context found."]
        
        # Step B: Build an augmented prompt containing our private database reference data
        augmented_prompt = f"""
        You are an official corporate HR assistant. Answer the user's question using ONLY the provided corporate context.
        If the answer cannot be found in the context, politely state that you do not know.
        
        Corporate Context:
        {retrieved_context}
        
        User Question: {request.message}
        """
        
        # Step C: Route the augmented prompt package to Google Gemini
        response = client.models.generate_content(
            model="models/gemini-3.8-flash",
            contents=augmented_prompt,
        )
        return {
            "response": response.text,
            "source_used": retrieved_context  # Return the database source row to verify it worked
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
