import json
import boto3
import os
from shared import db_service
from llm_service import llm_service

# Initialize clients
aws_endpoint = os.getenv("AWS_ENDPOINT_URL")
if aws_endpoint:
    s3 = boto3.client('s3', endpoint_url=aws_endpoint)
else:
    s3 = boto3.client('s3')

BUCKET_NAME = os.getenv('BUCKET_NAME')

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    for record in event['Records']:
        try:
            body = json.loads(record['body'])
            job_id = body['job_id']
            chunk_index = body['chunk_index']
            chunk_s3_key = body['chunk_s3_key']
            chunk_filename = body['chunk_filename']
            
            print(f"Analyzing job {job_id}, chunk {chunk_index}")
            
            # Download chunk
            local_path = f"/tmp/{chunk_filename}"
            s3.download_file(BUCKET_NAME, chunk_s3_key, local_path)
            
            # Analyze
            try:
                results = llm_service.analyze_chunk(local_path)
                
                chunk_result = {
                    "chunk_index": chunk_index,
                    "chunk_filename": chunk_filename,
                    "status": "completed",
                    "general_analyst": results.get("general_analyst"),
                    "striking": results.get("striking"),
                    "grappling": results.get("grappling"),
                    "submission": results.get("submission"),
                    "movement": results.get("movement"),
                    "head_coach": results.get("head_coach")
                }
                
                db_service.update_analysis_progress(job_id, chunk_result)
                
            except Exception as e:
                print(f"Analysis failed for chunk {chunk_index}: {e}")
                chunk_result = {
                    "chunk_index": chunk_index,
                    "chunk_filename": chunk_filename,
                    "status": "failed",
                    "error": str(e)
                }
                db_service.update_analysis_progress(job_id, chunk_result)
                raise e
            
            # Cleanup
            if os.path.exists(local_path):
                os.remove(local_path)
                
        except Exception as e:
            print(f"Error processing record: {e}")
            raise e
