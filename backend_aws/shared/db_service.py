import boto3
import os
import json
from datetime import datetime, timedelta
from decimal import Decimal
from botocore.exceptions import ClientError

# Initialize DynamoDB resource
# Use endpoint_url if provided (for local testing)
dynamodb_endpoint = os.getenv("DYNAMODB_ENDPOINT")
if dynamodb_endpoint:
    dynamodb = boto3.resource('dynamodb', endpoint_url=dynamodb_endpoint)
else:
    dynamodb = boto3.resource('dynamodb')

TABLE_NAME = os.getenv("TABLE_NAME", "pvhack-jobs")
table = dynamodb.Table(TABLE_NAME)

def create_job(job_id: str, s3_key: str):
    """Create a new job in DynamoDB"""
    try:
        now = datetime.now()
        expires_at = int((now + timedelta(days=30)).timestamp())
        
        item = {
            "job_id": job_id,
            "s3_key": s3_key,
            "split_status": "pending",
            "analysis_status": "pending",
            "total_chunks": 0,
            "completed_chunks": 0,
            "analyzed_chunks": 0,
            "split_pct": Decimal(0),
            "analysis_pct": Decimal(0),
            "chunks": [],
            "chunk_analyses": [],
            "created_at": now.isoformat(),
            "expires_at": expires_at
        }
        
        table.put_item(Item=item)
        return item
    except ClientError as e:
        print(f"Error creating job: {e}")
        raise e

def get_job(job_id: str):
    """Get job details from DynamoDB"""
    try:
        response = table.get_item(Key={"job_id": job_id})
        return response.get("Item")
    except ClientError as e:
        print(f"Error getting job: {e}")
        raise e

def update_split_progress(job_id: str, total_chunks=None, completed_chunks=None, split_pct=None, split_status=None, chunks_append=None):
    """Update split progress atomically"""
    try:
        update_expression = "SET"
        expression_attribute_values = {}
        expression_attribute_names = {}
        
        updates = []
        if total_chunks is not None:
            updates.append("#tc = :tc")
            expression_attribute_names["#tc"] = "total_chunks"
            expression_attribute_values[":tc"] = total_chunks
            
        if completed_chunks is not None:
            updates.append("#cc = :cc")
            expression_attribute_names["#cc"] = "completed_chunks"
            expression_attribute_values[":cc"] = completed_chunks
            
        if split_pct is not None:
            updates.append("#sp = :sp")
            expression_attribute_names["#sp"] = "split_pct"
            expression_attribute_values[":sp"] = split_pct # Decimal(str(split_pct)) might be needed if float issues arise
            
        if split_status is not None:
            updates.append("#ss = :ss")
            expression_attribute_names["#ss"] = "split_status"
            expression_attribute_values[":ss"] = split_status
            
        if chunks_append is not None:
            # Append to list if it exists, or create new list if not (using list_append)
            # Note: chunks must be initialized as empty list in create_job
            updates.append("#c = list_append(#c, :ca)")
            expression_attribute_names["#c"] = "chunks"
            expression_attribute_values[":ca"] = [chunks_append]

        if not updates:
            return

        update_expression += " " + ", ".join(updates)
        
        table.update_item(
            Key={"job_id": job_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
    except ClientError as e:
        print(f"Error updating split progress: {e}")
        raise e

def update_analysis_progress(job_id: str, chunk_result: dict):
    """Update analysis progress and append result"""
    try:
        # First get current state to calculate percentage
        # In a real high-concurrency scenario, we might want to use atomic counters, 
        # but for this use case, reading first is acceptable or we can trust the caller to provide counts.
        # However, to be safe and atomic, we can increment analyzed_chunks.
        
        # We need to fetch total_chunks to calculate percentage
        job = get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
            
        total_chunks = job.get("total_chunks", 1) # Avoid division by zero
        analyzed_chunks = job.get("analyzed_chunks", 0) + 1
        analysis_pct = (analyzed_chunks / total_chunks) * 100
        
        analysis_status = "processing"
        if analyzed_chunks >= total_chunks:
            analysis_status = "completed"
            
        update_expression = "SET #ac = :ac, #ap = :ap, #as = :as, #ca = list_append(#ca, :cr)"
        expression_attribute_names = {
            "#ac": "analyzed_chunks",
            "#ap": "analysis_pct",
            "#as": "analysis_status",
            "#ca": "chunk_analyses"
        }
        expression_attribute_values = {
            ":ac": analyzed_chunks,
            ":ap": str(analysis_pct), # Store as string or Decimal to avoid float errors
            ":as": analysis_status,
            ":cr": [chunk_result]
        }
        
        table.update_item(
            Key={"job_id": job_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
    except ClientError as e:
        print(f"Error updating analysis progress: {e}")
        raise e
