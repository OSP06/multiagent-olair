from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.routes.chat import router as chat_router
from api.routes.crm import router as crm_router
from api.routes.upload import router as upload_router
from crm.db import Base, engine
from crm import models 

# Load environment variables
load_dotenv()

# Create DB tables from models
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="MultiAgent-OLAIR Backend")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ✅ Allow only your React frontend http://localhost:3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router, prefix="/api/routes/chat", tags=["Chat"])
app.include_router(crm_router, prefix="/api/routes/crm", tags=["CRM"])
app.include_router(upload_router, prefix="/api/routes/upload", tags=["Upload"])

# Health check root
@app.get("/")
def root():
    return {"message": "MultiAgent OLAIR backend is live!"}
