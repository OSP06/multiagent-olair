# api/routes/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from utils.file_utils import load_internal_knowledge_base, load_commercial_lease_csv
import os

router = APIRouter()

UPLOAD_DIR = "data/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/docs")
def upload_docs(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    return {"filename": file.filename, "message": "✅ File uploaded successfully."}


@router.get("/internal-knowledge")
def load_kb(type: str = Query("qa", enum=["qa", "property"])):
    """
    Load the appropriate internal KB file based on the type.
    Only 'qa' and 'property' types are allowed for viewing.
    """
    file_map = {
        "qa": "qa_internal_kb.csv",
        "property": "HackathonInternalKnowledgeBase.csv"
    }

    filename = file_map.get(type)
    filepath = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")

    try:
        if type == "qa":
            kb = load_internal_knowledge_base(filepath)
        else:  # property
            kb = load_commercial_lease_csv(filepath)

        return {
            "type": type,
            "message": f"✅ Loaded {filename}",
            "count": len(kb),
            "sample": kb[:3]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to load: {e}")

        