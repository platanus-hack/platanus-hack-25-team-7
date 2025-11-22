# Project idea/description

Build an AI application that receives a 30-second video clip of an sport (in loop until the end of the video), analyzes it retroactively, and identifies:

- Key frames & key moments 
- Technical errors
- Defensive vulnerabilities
- Offensive opportunities
- specific issues on the practice of the sport
- Fatigue indicators
- Tactical recommendations for the next time

The system does NOT replace the coach. It acts as a real-time companion or assistant, providing quick analytical insights to complement human decision-making between rounds. This works specially for non profesional sprorts practitioners that do not have access to high level coaching.

# Goals

- Deliver fast, reliable, explainable insights in < 10 seconds
- Provide actionable recommendations a coach can use under time pressure
- Enable a fighter to gain super-rapid analytics normally only available via post-fight review
- Build a future foundation for real-time recognition of strikes, grappling transitions, and fight context

# Requirements
- FR-01: Video Upload
    - The user can upload a 30s video clip (from phone or URL).
    - Supported formats: MP4, MOV, WebM.
- FR-02: Automatic Keyframe Extraction by LLM
    - Video is send to LLM to extract top 3-7 key frames based on sport necessities.
- FR-03: Technical Analysis by LLM
    - System analyzes key frames + motion summary to identify critical moments.
- FR-04: Error Detection by LLM for Sport-Specific Issues
    - Identify technical errors, defensive vulnerabilities, offensive opportunities, fatigue indicators.
- FR-05: Recommendations by LLM
    - Generated output includes:
        - "Top 3 mistakes this round"
        - "Top 3 adjustments for next match"
        - One tactical recommendation ("Stay outside his lead leg", "Look for counter right cross", etc.)
- FR-06: Output Visualization
    - Show key frames with visual annotations
    - Show timeline of action intensity
    - Show text summary

# Demo:

- Scenario
    - A coach/sport practicioner uploads the video of todays practice.
- Steps
    - User starts recording using the app
    - System after 30 seconds send to llm model to extract key points asyncronously
    - App extracts key frames + action spikes
    - Repeat until end of the video
    - Rocompile all key points from each 30 seconds interval and generate a summary analysis
    - Analysis is generated
    - Recommendations:
    - User reviews annotated frames + summary
- Expected Outcome
    - Coach uses insights to instruct player during the break before next practice.


## Phase 1 - MVP (Core Loop)
    
- 30s Video Capture Loop
    - User starts recording.
    - App collects 30s chunks continuously until Video Ends.
    - Each chunk is uploaded asynchronously.
- Lightweight Keyframe Extraction
    - Extract 3-7 keyframes per 30s segment using LLM model to detect key frames.
- Chunk-Level LLM Analysis
    - For each 30s chunk, send keyframes + motion summary to the LLM.
    - LLM returns: key moments, errors, opportunities, quick recommendations.
- End-of-Round Summary
    - System aggregates all 30s insights.
    - Generates:
        - Top 3 mistakes
        - Top 3 adjustments
        - 1 tactical recommendation
        - Key annotated frames
- Basic UI
    - Record screen
    - Analysis progress
    - Summary screen with text + frames
## Phase 2:


txt
/mma-ai-app
  frontend/
     public/
        favicon.ico
        index.html
     src/
        components/
           VideoRecorder.jsx
           UploadButton.jsx
           AnalysisProgress.jsx
           SummaryView.jsx
        pages/
           Home.jsx
           Record.jsx
           Analysis.jsx
        hooks/
           useRecorder.js
        utils/
           api.js
        App.jsx
        main.jsx
     .env
     package.json
     vite.config.js
     README.md
  /backend
    /video_processing
    /keyframe_extractor
    /planner (LLM-based reasoning)
  /models
    - keyframe_model
    - recommendation_llm
  /outputs
    - reports
    - annotated_frames
  /infrastructure
    - container configs
    - cloud deployment

# Project structure


- Frontend
    - Next.js / React
    - ShadCN UI
    - Tailwind
- Backend
    - Python (FastAPI)
    - FFmpeg (video preprocessing)
- AI / ML
    - LLM (OpenAI or Llama) for tactical recommendations
- Storage
    - AWS S3 (video + images)
    - PostgreSQL for users & metadata
- Infra
    - Docker
    - AWS Lambda or ECS
    - GPU inference (AWS G4dn or local GTX/RTX)
# Tech stack
- Backend: Python, LangGraph