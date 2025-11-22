import os
import re
import subprocess
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JOBS = {}
JOBS_FILE = "jobs.json"

def save_jobs():
    """Save JOBS dict to jobs.json"""
    try:
        with open(JOBS_FILE, "w") as f:
            json.dump(JOBS, f, indent=2)
        logger.info(f"JOBS saved to {JOBS_FILE}")
    except Exception as e:
        logger.error(f"Error saving JOBS: {e}")

def load_jobs():
    """Load JOBS dict from jobs.json if exists"""
    global JOBS
    if os.path.exists(JOBS_FILE):
        try:
            with open(JOBS_FILE, "r") as f:
                JOBS = json.load(f)
            logger.info(f"JOBS loaded from {JOBS_FILE}")
        except Exception as e:
            logger.error(f"Error loading JOBS: {e}")
            JOBS = {}
    else:
        logger.info(f"No existing {JOBS_FILE} found, starting fresh")

# Load existing jobs on module import
load_jobs()

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
            logger.info(f"[{datetime.now().isoformat()}] Starting split for job {job_id}")
            JOBS[job_id]["split_status"] = "processing"
            save_jobs()
            
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
                JOBS[job_id]["analysis_status"] = "failed"
                save_jobs()
                return

            window = 30
            total_chunks = int(duration // window) + (1 if duration % window > 0 else 0)
            
            JOBS[job_id]["total_chunks"] = total_chunks
            save_jobs()
            
            chunks = []
            chunk_paths = []  # Store full paths for analysis
            
            # Step 1: Split all chunks
            logger.info(f"[{datetime.now().isoformat()}] Splitting video into {total_chunks} chunks...")
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
                chunk_paths.append(chunk_path)
                JOBS[job_id]["completed_chunks"] = i + 1
                JOBS[job_id]["split_pct"] = ((i + 1) / total_chunks) * 100
                
            JOBS[job_id]["chunks"] = chunks
            JOBS[job_id]["split_status"] = "completed"
            logger.info(f"[{datetime.now().isoformat()}] Split completed for job {job_id}")
            save_jobs()
            
            # Step 2: Analyze chunks with LLM (sequential analysis)
            logger.info(f"[{datetime.now().isoformat()}] Starting LLM analysis for {total_chunks} chunks...")
            JOBS[job_id]["analysis_status"] = "processing"
            save_jobs()
            
            from services.llm_service import llm_service
            
            analyzed_count = 0
            failed_count = 0
            
            for i, (chunk_filename, chunk_path) in enumerate(zip(chunks, chunk_paths)):
                chunk_analysis = {
                    "chunk_index": i,
                    "chunk_filename": chunk_filename,
                    "status": "processing",
                    "general_analyst": None,
                    "striking": None,
                    "grappling": None,
                    "submission": None,
                    "error": None
                }
                
                try:
                    logger.info(f"[{datetime.now().isoformat()}] Analyzing chunk {i+1}/{total_chunks}: {chunk_filename}")
                    
                    # Call LLM service (sequential, includes delays between analyses)
                    results = llm_service.analyze_chunk(chunk_path)
                    
                    # Store results
                    chunk_analysis["general_analyst"] = results.get("general_analyst")
                    chunk_analysis["striking"] = results.get("striking")
                    chunk_analysis["grappling"] = results.get("grappling")
                    chunk_analysis["submission"] = results.get("submission")
                    chunk_analysis["status"] = "completed"
                    analyzed_count += 1
                    
                    logger.info(f"[{datetime.now().isoformat()}] Chunk {i+1}/{total_chunks} analysis completed")
                    
                except Exception as e:
                    logger.error(f"[{datetime.now().isoformat()}] Analysis failed for chunk {i+1}: {e}")
                    chunk_analysis["status"] = "failed"
                    chunk_analysis["error"] = str(e)
                    failed_count += 1
                
                # Add to chunk_analyses list
                JOBS[job_id]["chunk_analyses"].append(chunk_analysis)
                
                # Update progress
                JOBS[job_id]["analyzed_chunks"] = analyzed_count + failed_count
                JOBS[job_id]["analysis_pct"] = ((analyzed_count + failed_count) / total_chunks) * 100
                save_jobs()
            
            # Step 3: Determine final analysis status
            if failed_count == 0:
                JOBS[job_id]["analysis_status"] = "completed"
            elif failed_count > total_chunks / 2:
                JOBS[job_id]["analysis_status"] = "failed"
            else:
                JOBS[job_id]["analysis_status"] = "partial"
            
            logger.info(f"[{datetime.now().isoformat()}] Analysis completed for job {job_id}: {analyzed_count} succeeded, {failed_count} failed")
            save_jobs()
            
        except Exception as e:
            logger.error(f"[{datetime.now().isoformat()}] Error in split_video_background: {e}")
            JOBS[job_id]["split_status"] = "failed"
            JOBS[job_id]["analysis_status"] = "failed"
            save_jobs()

video_service = VideoService()
