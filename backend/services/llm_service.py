import os
import time
import logging
from typing import Dict, Optional
import json
from google import genai
from dotenv import load_dotenv
from datetime import datetime
from prompts import (
    generate_general_analyst_prompt,
    generate_specialist_prompt,
    generate_head_coach_aggregation_prompt,
    generate_structured_segment_prompt,
    generate_tactical_coach_structured_prompt,
)
from models.schemas import SegmentSummary, TacticalCoachSummary

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
        
        # Use environment variable for model, default to gemini-2.5-flash
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Default config for all LLM calls
        self.default_config = {
            "temperature": 0.0,
            "topP": 0.95,
            "seed": 42
        }

    def upload_file(self, file_path, max_retries=3):
        """Upload file to Gemini with retry logic and timeout"""
        for attempt in range(max_retries):
            try:
                logger.info(f"[{datetime.now().isoformat()}] Uploading file (attempt {attempt + 1}/{max_retries}): {file_path}")
                myfile = self.client.files.upload(file=file_path)
                
                # Poll for processing completion with 2-minute timeout
                start_time = time.time()
                timeout = 120  # 2 minutes
                
                while myfile.state.name == "PROCESSING":
                    elapsed = time.time() - start_time
                    if elapsed > timeout:
                        raise TimeoutError(f"File processing timeout after {timeout}s")
                    
                    logger.info(f"Processing video... ({int(elapsed)}s elapsed)")
                    time.sleep(5)
                    myfile = self.client.files.get(name=myfile.name)
                    
                if myfile.state.name == "FAILED":
                    raise ValueError(f"File processing failed: {myfile.state.name}")
                    
                logger.info(f"[{datetime.now().isoformat()}] File uploaded and processed: {myfile.name}")
                return myfile
                
            except Exception as e:
                logger.error(f"Upload attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise e

    def analyze_chunk(self, file_path: str, segment_index: int, start_s: int, end_s: int):
        """
        Analyze chunk following the workflow from notebook:
        1. General Analyst creates ground truth from video
        2. Specialists analyze the ground truth (text only, no video)
        3. Head Coach aggregates all specialist analyses
        
        Args:
            file_path: Path to video file
        
        Returns:
            Dict with analysis results
        """
        if not self.client:
            raise ValueError("GEMINI_API_KEY not set or client initialization failed")

        try:
            myfile = self.upload_file(file_path)
            
            results = {}
            
            # Step 1: General Analyst
            logger.info(f"[{datetime.now().isoformat()}] Running General Analyst...")
            prompt_general = generate_general_analyst_prompt()
            response_general = self.client.models.generate_content(
                model=self.model, 
                contents=[myfile, prompt_general],
                config=self.default_config
            )
            general_analysis = response_general.text
            results["general_analyst"] = general_analysis

            # Structured SegmentSummary JSON generation
            try:
                structured_prompt = generate_structured_segment_prompt(
                    general_analyst_table=general_analysis,
                    segment_index=segment_index,
                    start_s=start_s,
                    end_s=end_s,
                )
                struct_response = self.client.models.generate_content(
                    model=self.model,
                    contents=[structured_prompt],
                    config={**self.default_config, "response_mime_type": "application/json", "response_json_schema": SegmentSummary.model_json_schema()},
                )
                raw_json = struct_response.text.strip()
                segment_summary_obj: Optional[SegmentSummary] = None
                try:  # Validación directa si JSON limpio
                    segment_summary_obj = SegmentSummary.model_validate_json(raw_json)
                except Exception as e_json:
                    logger.warning(f"Initial SegmentSummary parse failed: {e_json}; retrying correction")
                    correction_prompt = structured_prompt + f"\nEl JSON anterior fue inválido ({e_json}). Devuelve SOLO JSON corregido."
                    struct_response = self.client.models.generate_content(
                        model=self.model,
                        contents=[correction_prompt],
                        config={**self.default_config, "response_mime_type": "application/json", "response_json_schema": SegmentSummary.model_json_schema()},
                    )
                    raw_json = struct_response.text.strip()
                    try:
                        segment_summary_obj = SegmentSummary.model_validate_json(raw_json)
                    except Exception as e_json2:
                        logger.error(f"Failed to parse SegmentSummary after correction: {e_json2}")
                if segment_summary_obj:
                    results["segment_summary"] = segment_summary_obj.model_dump()
                else:
                    results["segment_summary_error"] = raw_json[:400]
            except Exception as e_struct:
                logger.error(f"Structured segment generation failed: {e_struct}")
            logger.info(f"[{datetime.now().isoformat()}] General Analyst completed")
            
            # Delay between LLM calls to avoid rate limits
            time.sleep(5)
            
            # Step 2: Specialist Roles
            specialist_roles = ["striking", "grappling", "submission", "movement"]
            specialist_analyses = {}
            
            for role in specialist_roles:
                logger.info(f"[{datetime.now().isoformat()}] Running {role} specialist analysis...")
                prompt_specialist = generate_specialist_prompt(
                    role=role,
                    general_analysis_text=general_analysis
                )
                response_specialist = self.client.models.generate_content(
                    model=self.model,
                    contents=[prompt_specialist],
                    config=self.default_config
                )
                specialist_analysis = response_specialist.text
                specialist_analyses[role] = specialist_analysis
                results[role] = specialist_analysis
                logger.info(f"[{datetime.now().isoformat()}] {role} specialist analysis completed")
                
                # Delay between specialist analyses
                time.sleep(5)
            
            # Step 3: Head Coach aggregation (text)
            logger.info(f"[{datetime.now().isoformat()}] Running Head Coach aggregation...")
            prompt_head_coach = generate_head_coach_aggregation_prompt(specialist_analyses)
            response_coach = self.client.models.generate_content(
                model=self.model,
                contents=[prompt_head_coach],
                config=self.default_config
            )
            results["head_coach"] = response_coach.text
            logger.info(f"[{datetime.now().isoformat()}] Head Coach aggregation completed")
                
            return results
            
        except Exception as e:
            logger.error(f"[{datetime.now().isoformat()}] Error in analyze_chunk: {e}")
            raise e

llm_service = LLMService()
