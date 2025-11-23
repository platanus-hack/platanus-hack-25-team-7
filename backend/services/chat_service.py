from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    message_to_dict, messages_to_dict, messages_from_dict
)
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver, MemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
import os, uuid, re
from pathlib import Path
import random

load_dotenv()

llm_orchestrator = init_chat_model(
    "us.amazon.nova-pro-v1:0",
    model_provider="bedrock_converse",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRETS_ACCESS_KEY"),
)
llm_light = init_chat_model(
    "us.meta.llama3-1-70b-instruct-v1:0",
    model_provider="bedrock_converse",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRETS_ACCESS_KEY"),
)


# -----------------------------------------------------------------------------
# Video-in-depth analysis tools
# -----------------------------------------------------------------------------
# @tool
# def cut_video(video_path: str, start_time: float, end_time: float) -> str:
#     """Cut the video using ffmpeg or any fastest library and return the video path (in local folder)"""
#     pass


# @tool
# def make_video_question(question: str, video_path: str) -> str:
#     """Make a question to the video-capable LLM (Gemini or other) about the video provided and return the answer."""
#     # gemini_video_llm = ...
#     pass


# -----------------------------------------------------------------------------
# Specialists exploration
# -----------------------------------------------------------------------------

@tool
def get_availables_specialists() -> str:
    """List all the available specialists for video analysis. The specialists prompts are located in the 'prompts' folder (recursively)."""
    
    prompts_folder = Path(__file__).parent.parent / "prompts"
    
    if not prompts_folder.exists():
        return "No specialists available. Prompts folder not found."
    
    specialists = []
    for file_path in prompts_folder.rglob("*.txt"):
        specialist_name = file_path.stem
        specialists.append(specialist_name)
    
    for file_path in prompts_folder.rglob("*.md"):
        specialist_name = file_path.stem
        specialists.append(specialist_name)
    
    if not specialists:
        return "No specialist prompts found in the prompts folder."
    
    return f"Available specialists: {', '.join(sorted(set(specialists)))}"


@tool
def explain_specialist_analysis(specialist_name: str, video_context: str) -> str:
    """Explain the analysis made by the specialist LLM prompt (get prompt saved) based on the video context provided."""
    prompts_folder = Path(__file__).parent.parent / "prompts"
    
    # Search for the specialist prompt file
    specialist_file = None
    for ext in ['.txt', '.md']:
        potential_path = prompts_folder / f"{specialist_name}{ext}"
        if potential_path.exists():
            specialist_file = potential_path
            break
    
    # Also search recursively in subfolders
    if not specialist_file:
        for file_path in prompts_folder.rglob(f"{specialist_name}.*"):
            if file_path.suffix in ['.txt', '.md']:
                specialist_file = file_path
                break
    
    if not specialist_file:
        return f"Specialist '{specialist_name}' not found. Use get_availables_specialists to see available options."
    
    # Read the specialist prompt
    with open(specialist_file, 'r', encoding='utf-8') as f:
        specialist_prompt = f.read()
    
    # Create explanation prompt
    explanation_prompt = f"""Based on this specialist prompt:

{specialist_prompt}

And this video context:
{video_context}

Explain what kind of analysis this specialist would provide and what insights they would focus on."""
    
    # Use the LLM to generate explanation
    response = llm_light.invoke(explanation_prompt, performanceConfig={"latency": "optimized"}, max_tokens=256, temperature=0)
    return response.content


@tool
def consult_specialist(specialist_name: str, question: str, video_context: str) -> str:
    """Consult the specialist LLM prompt/call (get prompt saved) with the question provided."""
    prompts_folder = Path(__file__).parent.parent / "prompts"
    
    # Search for the specialist prompt file
    specialist_file = None
    for ext in ['.txt', '.md']:
        potential_path = prompts_folder / f"{specialist_name}{ext}"
        if potential_path.exists():
            specialist_file = potential_path
            break
    
    # Also search recursively in subfolders
    if not specialist_file:
        for file_path in prompts_folder.rglob(f"{specialist_name}.*"):
            if file_path.suffix in ['.txt', '.md']:
                specialist_file = file_path
                break
    
    if not specialist_file:
        return f"Specialist '{specialist_name}' not found. Use get_availables_specialists to see available options."
    
    # Read the specialist prompt
    with open(specialist_file, 'r', encoding='utf-8') as f:
        specialist_prompt = f.read()
    
    # Construct the full consultation prompt
    full_prompt = f"""{specialist_prompt}

Video Context:
{video_context}

Question:
{question}

Provide a detailed analysis based on your expertise."""
    
    # Invoke the LLM with the specialist's perspective
    response = llm_light.invoke(full_prompt, performanceConfig={"latency": "optimized"}, max_tokens=256, temperature=0)
    return response.content


# -----------------------------------------------------------------------------
# New prompt creation
# -----------------------------------------------------------------------------

@tool
def create_prompt_for_other_topic(topic: str, details: str) -> str:
    """Create a prompt for other topics/sports videos beyond just MMA analysis."""
    creation_prompt = f"""Create a specialist prompt for analyzing {topic} videos.

Details about what this specialist should focus on:
{details}

Generate a comprehensive prompt that defines:
1. The specialist's expertise and role
2. Key aspects to analyze in the video
3. Common errors or issues to identify
4. Recommendations format

Return only the prompt content, ready to be saved."""
    
    response = llm_light.invoke(creation_prompt, max_tokens=512, temperature=0.7)
    return response.content


@tool
def create_specialist_prompt(specialist_name: str, question: str, video_context: str = "") -> str:
    """Create a prompt for a specific specialist based on the provided name, question, and video context. You need to use one random prompt template from the 'prompts' folder as inspiration."""
    prompts_folder = Path(__file__).parent.parent / "prompts"
    
    # Get a random existing prompt as template
    template_content = ""
    template_files = list(prompts_folder.rglob("*.txt")) + list(prompts_folder.rglob("*.md"))
    
    if template_files:
        template_file = random.choice(template_files)
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
    
    creation_prompt = f"""Create a specialist prompt for: {specialist_name}

Use this existing template as inspiration for structure and format:
---
{template_content}
---

The specialist should address this question: {question}

{"Video context: " + video_context if video_context else ""}

Generate a prompt that:
1. Defines the specialist's expertise
2. Lists key analysis points
3. Specifies output format
4. Includes relevant technical knowledge

Return only the prompt content."""
    
    response = llm_light.invoke(creation_prompt, max_tokens=512, temperature=0.7)
    return response.content


@tool
def save_specialist_prompt(specialist_name: str, prompt_content: str) -> str:
    """Save the specialist prompt content into a file in the 'prompts' folder with the given specialist name."""
    prompts_folder = Path(__file__).parent.parent / "prompts" / "templates"
    prompts_folder.mkdir(parents=True, exist_ok=True)
    
    specialist_file = prompts_folder / f"{specialist_name}.txt"
    
    with open(specialist_file, 'w', encoding='utf-8') as f:
        f.write(prompt_content)
    
    return f"Specialist prompt '{specialist_name}' saved successfully."


# -----------------------------------------------------------------------------
# Agent setup
# -----------------------------------------------------------------------------

SYSTEM_PROMPT_TEMPLATE = """
<core_identity>
You are a sports video analysis orchestrator that analyzes videos in-depth by asking questions to a video-capable LLM, cutting videos into segments for detailed examination, and creating specialized prompts for various sports including MMA, with all interactions saved for future reference.
""" + f"""
Today is {datetime.now().strftime('%Y-%m-%d')}.\n
</core_identity>
"""

USER_MESSAGE_TEMPLATE = """
<video_context_analysis>
{video_context_analysis}
</video_context_analysis>

<user_query>
{user_query}
</user_query>
"""

prompt_template = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT_TEMPLATE), ("user", USER_MESSAGE_TEMPLATE)]
)

react_agent = create_react_agent(
    model=llm_orchestrator,
    tools=[
        get_availables_specialists, 
        consult_specialist, 
        explain_specialist_analysis,
        create_prompt_for_other_topic, 
        create_specialist_prompt, 
        save_specialist_prompt
    ],
    debug=False,
    # response_format=,     # PyDantic Class
    checkpointer=InMemorySaver(),
    store=InMemoryStore(),
)


def call_agent(user_query: str, video_context_analysis: str = "", thread_id: str = ""):
    """
    thread_id: Unique identifier for the interaction thread (video_path or user session)
    """
    if not thread_id:
        thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 10, "max_tokens": 256}

    ai_response = react_agent.invoke(input=prompt_template.invoke({
        "video_context_analysis": video_context_analysis, "user_query": user_query
    }), config=config,)['messages'][-1].content

    ai_response = re.sub(r'<thinking>.*?</thinking>', '', ai_response, flags=re.DOTALL).strip()
    
    return ai_response


if __name__ == "__main__":
    # r = call_agent("Hola")
    # r = call_agent("List all the available specialists for video analysis.")
    r = call_agent("What does the general_analyst specialist do? Explain their role and what kind of analysis they provide.")
    print(r)
