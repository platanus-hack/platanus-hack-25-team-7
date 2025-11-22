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

class ChunkAnalysis(BaseModel):
    chunk_index: int
    chunk_filename: str
    status: str  # "pending", "processing", "completed", "failed", "timeout"
    general_analyst: Optional[str] = None
    striking: Optional[str] = None
    grappling: Optional[str] = None
    submission: Optional[str] = None
    error: Optional[str] = None

class AnalysisProgress(BaseModel):
    job_id: str
    split_status: str
    analysis_status: str  # "pending", "processing", "completed", "partial", "failed"
    total_chunks: int
    analyzed_chunks: int
    analysis_pct: float
    chunk_analyses: List[ChunkAnalysis] = []
