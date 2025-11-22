from pydantic import BaseModel
from typing import List, Optional

class UploadResponse(BaseModel):
    job_id: str
    message: str
    status: str

class SplitProgress(BaseModel):
    job_id: str
    split_status: str
    total_chunks: int
    completed_chunks: int
    split_pct: float
    chunks: List[str] = []
