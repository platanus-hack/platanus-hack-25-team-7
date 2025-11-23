from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import uuid
import json
import os
import boto3
from schemas import UploadResponse, SplitProgress, AnalysisProgress
from shared import db_service
from services.chat_service import call_agent as chat_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQS client
# Use endpoint_url if provided (for local testing)
sqs_endpoint = os.getenv("AWS_ENDPOINT_URL") # Generic endpoint or specific SQS one?
if sqs_endpoint:
    sqs = boto3.client("sqs", endpoint_url=sqs_endpoint)
else:
    sqs = boto3.client("sqs")

SPLIT_QUEUE_URL = os.getenv("SPLIT_QUEUE_URL")

@app.post("/upload", response_model=UploadResponse)
async def upload_video(s3_key: str = Body(..., embed=True)):
    job_id = str(uuid.uuid4())
    
    # Create job in DynamoDB
    try:
        db_service.create_job(job_id, s3_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Send to Split Queue
    message_body = {
        "job_id": job_id,
        "s3_key": s3_key
    }
    
    try:
        sqs.send_message(
            QueueUrl=SPLIT_QUEUE_URL,
            MessageBody=json.dumps(message_body),
            MessageGroupId=job_id,
            MessageDeduplicationId=job_id 
        )
    except Exception as e:
        # If SQS fails, we might want to delete the job or mark it failed?
        # For now just raise error
        raise HTTPException(status_code=500, detail=f"Queue error: {str(e)}")
    
    return UploadResponse(job_id=job_id, message="Processing started", status="processing")

@app.get("/agent/{job_id}")
async def call_agent(job_id: str, question: str):
    job = db_service.get_job(job_id)
    videos = job.get("chunk_analyses", []) if job else []
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    response = chat_agent(question, videos)
    return {"response": response}

@app.get("/split/{job_id}", response_model=SplitProgress)
async def get_split_progress(job_id: str):
    job = db_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return SplitProgress(**job)

@app.get("/analysis/{job_id}", response_model=AnalysisProgress)
async def get_analysis_progress(job_id: str):
    job = db_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return AnalysisProgress(**job)
