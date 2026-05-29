from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
from datetime import datetime
import os
import uuid

load_dotenv()

client = CosmosClient(
    url=os.getenv("COSMOS_ENDPOINT"),
    credential=os.getenv("COSMOS_KEY")
)

users_database = client.get_database_client(os.getenv("COSMOS_USERS_DATABASE"))
contacts_container = users_database.get_container_client(os.getenv("COSMOS_CONTACTS_CONTAINER", "contacts"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    company: str = ""
    message: str

@app.post("/contact", status_code=201)
def save_contact(payload: ContactRequest):
    try:
        item = {
            "id": str(uuid.uuid4()),
            "type": "contact",
            "name": payload.name,
            "email": payload.email,
            "company": payload.company,
            "message": payload.message,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
        }
        contacts_container.upsert_item(item)
        return {"message": "Contato salvo com sucesso.", "id": item["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Não foi possível salvar o contato.")

#For testing: python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000