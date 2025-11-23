import json
import boto3
import os
import subprocess
import math
import re
import imageio_ffmpeg
from shared import db_service

# Initialize clients
aws_endpoint = os.getenv("AWS_ENDPOINT_URL")
if aws_endpoint:
    s3 = boto3.client('s3', endpoint_url=aws_endpoint)
    sqs = boto3.client('sqs', endpoint_url=aws_endpoint)
else:
    s3 = boto3.client('s3')
    sqs = boto3.client('sqs')

BUCKET_NAME = os.getenv('BUCKET_NAME')
ANALYSIS_QUEUE_URL = os.getenv('ANALYSIS_QUEUE_URL')

def get_duration(ffmpeg_exe, file_path):
    """Get duration using ffmpeg -i"""
    cmd = [ffmpeg_exe, "-i", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # ffmpeg outputs to stderr
    output = result.stderr
    match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})", output)
    if match:
        hours, minutes, seconds = match.groups()
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    raise ValueError(f"Could not determine duration from output: {output}")

def lambda_handler(event, context):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    for record in event['Records']:
        try:
            body = json.loads(record['body'])
            job_id = body['job_id']
            s3_key = body['s3_key']
            
            print(f"Processing job {job_id}, key {s3_key}")
            
            # Download video
            local_path = f"/tmp/{job_id}.mp4"
            s3.download_file(BUCKET_NAME, s3_key, local_path)
            
            # Get duration
            try:
                duration = get_duration(ffmpeg_exe, local_path)
            except ValueError as e:
                print(f"Error getting duration: {e}")
                raise e
            
            window = 30
            total_chunks = int(duration // window) + (1 if duration % window > 0 else 0)
            
            db_service.update_split_progress(job_id, total_chunks=total_chunks, split_status="processing")
            
            for i in range(total_chunks):
                start_time = i * window
                end_time = min((i + 1) * window, duration)
                
                chunk_filename = f"chunk_{i}.mp4"
                chunk_path = f"/tmp/{chunk_filename}"
                chunk_s3_key = f"splits/{job_id}/{chunk_filename}"
                
                # Split
                split_cmd = [
                    ffmpeg_exe, "-y",
                    "-ss", str(start_time),
                    "-to", str(end_time),
                    "-i", local_path,
                    "-c", "copy",
                    chunk_path
                ]
                subprocess.run(split_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Upload
                s3.upload_file(chunk_path, BUCKET_NAME, chunk_s3_key)
                
                # Update DB
                db_service.update_split_progress(
                    job_id, 
                    completed_chunks=i+1, 
                    split_pct=((i+1)/total_chunks)*100, 
                    chunks_append=chunk_filename
                )
                
                # Send to Analysis Queue
                sqs.send_message(
                    QueueUrl=ANALYSIS_QUEUE_URL,
                    MessageBody=json.dumps({
                        "job_id": job_id,
                        "chunk_index": i,
                        "chunk_s3_key": chunk_s3_key,
                        "chunk_filename": chunk_filename
                    }),
                    MessageGroupId=job_id
                )
                
                # Cleanup chunk
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)
                
            db_service.update_split_progress(job_id, split_status="completed")
            
            # Cleanup video
            if os.path.exists(local_path):
                os.remove(local_path)
                
        except Exception as e:
            print(f"Error processing record: {e}")
            # If we fail, the message will go back to queue (or DLQ eventually)
            # We might want to update DB status to failed?
            if 'job_id' in locals():
                try:
                    db_service.update_split_progress(job_id, split_status="failed")
                except:
                    pass
            raise e
