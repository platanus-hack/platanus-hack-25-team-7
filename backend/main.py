from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
import shutil
from services.video_service import video_service, JOBS
from models.schemas import UploadResponse, SplitProgress

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload", response_model=UploadResponse)
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(('.mp4', '.mov', '.webm')):
        raise HTTPException(status_code=400, detail="Invalid file format. Allowed: .mp4, .mov, .webm")
    
    job_id = str(uuid.uuid4())
    file_path = os.path.join(video_service.uploads_dir, f"{job_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Initialize job
    JOBS[job_id] = {
        "job_id": job_id,
        "split_status": "pending",
        "total_chunks": 0,
        "completed_chunks": 0,
        "split_pct": 0.0,
        "chunks": []
    }
    
    background_tasks.add_task(video_service.split_video_background, job_id, file_path, file.filename)
    
    return UploadResponse(job_id=job_id, message="Video uploaded and processing started", status="processing")

@app.get("/split/{job_id}", response_model=SplitProgress)
async def get_split_progress(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = JOBS[job_id]
    return SplitProgress(**job)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
