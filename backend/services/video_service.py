import os
import re
import subprocess
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JOBS = {}

class VideoService:
    def __init__(self):
        # Define paths relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.splits_dir = os.path.join(base_dir, "media", "splits")
        self.uploads_dir = os.path.join(base_dir, "media", "uploads")
        os.makedirs(self.splits_dir, exist_ok=True)
        os.makedirs(self.uploads_dir, exist_ok=True)

    def sanitize_filename(self, filename: str) -> str:
        # Remove extension first
        name = os.path.splitext(filename)[0]
        # Replace non-alphanumeric with underscore
        sanitized = re.sub(r'[^a-zA-Z0-9]', '_', name)
        return sanitized

    def split_video_background(self, job_id: str, video_path: str, original_filename: str):
        try:
            logger.info(f"Starting split for job {job_id}")
            JOBS[job_id]["split_status"] = "processing"
            
            sanitized_name = self.sanitize_filename(original_filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Get duration using ffprobe
            try:
                result = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                duration = float(result.stdout)
            except Exception as e:
                logger.error(f"Error getting duration: {e}")
                JOBS[job_id]["split_status"] = "failed"
                return

            window = 30
            total_chunks = int(duration // window) + (1 if duration % window > 0 else 0)
            
            JOBS[job_id]["total_chunks"] = total_chunks
            
            chunks = []
            
            for i in range(total_chunks):
                start_time = i * window
                end_time = min((i + 1) * window, duration)
                
                chunk_filename = f"{sanitized_name}_{timestamp}_chunk_{i+1}.mp4"
                chunk_path = os.path.join(self.splits_dir, chunk_filename)
                
                # Use ffmpeg to split
                cmd = [
                    "ffmpeg", "-y",
                    "-ss", str(start_time),
                    "-to", str(end_time),
                    "-i", video_path,
                    "-c", "copy",
                    chunk_path
                ]
                
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                chunks.append(chunk_filename)
                JOBS[job_id]["completed_chunks"] = i + 1
                JOBS[job_id]["split_pct"] = ((i + 1) / total_chunks) * 100
                
            JOBS[job_id]["chunks"] = chunks
            JOBS[job_id]["split_status"] = "completed"
            logger.info(f"Split completed for job {job_id}")
            
        except Exception as e:
            logger.error(f"Error splitting video: {e}")
            JOBS[job_id]["split_status"] = "failed"

video_service = VideoService()
