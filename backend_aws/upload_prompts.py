import boto3
import os
import sys
from pathlib import Path

def upload_prompts(bucket_name):
    """Uploads prompts from local templates folder to S3"""
    
    # Path to templates directory
    # Assuming this script is in backend_aws/
    base_dir = Path(__file__).parent.parent
    templates_dir = base_dir / "backend" / "prompts" / "templates"
    
    if not templates_dir.exists():
        print(f"Error: Templates directory not found at {templates_dir}")
        return

    s3 = boto3.client('s3')
    
    print(f"Uploading prompts to s3://{bucket_name}/prompts/ ...")
    
    for file_path in templates_dir.glob("*.txt"):
        key = f"prompts/{file_path.name}"
        try:
            print(f"Uploading {file_path.name} -> {key}")
            s3.upload_file(str(file_path), bucket_name, key)
            print("Success")
        except Exception as e:
            print(f"Failed to upload {file_path.name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python upload_prompts.py <bucket_name>")
        sys.exit(1)
    
    bucket_name = sys.argv[1]
    upload_prompts(bucket_name)
