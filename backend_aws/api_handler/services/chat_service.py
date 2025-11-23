from langchain_aws import ChatBedrockConverse
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
import os, uuid, re
import boto3
import random

# Initialize S3 client
s3_client = boto3.client("s3")
BUCKET_NAME = os.getenv("BUCKET_NAME")
PROMPTS_PREFIX = "prompts/templates/"

# Initialize Bedrock models
# We assume the Lambda execution role has permissions to invoke these models
llm_orchestrator = ChatBedrockConverse(
    model="us.amazon.nova-pro-v1:0",
    region_name="us-east-1", 
)

llm_light = ChatBedrockConverse(
    model="us.meta.llama3-1-70b-instruct-v1:0",
    region_name="us-east-1",
)

# Helper to read from S3
def _read_prompt_from_s3(key: str) -> str:
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        print(f"Error reading {key} from S3: {e}")
        return ""

# Helper to list prompts from S3
def _list_prompts_from_s3() -> list[str]:
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PROMPTS_PREFIX)
        if "Contents" not in response:
            return []
        
        prompts = []
        for obj in response["Contents"]:
            key = obj["Key"]
            if key.endswith(".txt") or key.endswith(".md"):
                # Extract filename without extension
                filename = key.split("/")[-1]
                name = filename.rsplit(".", 1)[0]
                prompts.append(name)
        return prompts
    except Exception as e:
        print(f"Error listing prompts from S3: {e}")
        return []

# Helper to find specific prompt key
def _find_specialist_key(specialist_name: str) -> str:
    # Try .txt and .md
    for ext in [".txt", ".md"]:
        key = f"{PROMPTS_PREFIX}{specialist_name}{ext}"
        try:
            s3_client.head_object(Bucket=BUCKET_NAME, Key=key)
            return key
        except:
            continue
    return None

# -----------------------------------------------------------------------------
# Specialists exploration
# -----------------------------------------------------------------------------

@tool
def get_availables_specialists() -> str:
    """List all the available specialists for video analysis."""
    specialists = _list_prompts_from_s3()
    
    if not specialists:
        return "No specialists available. Prompts folder not found or empty."
    
    return f"Available specialists: {', '.join(sorted(set(specialists)))}"


@tool
def explain_specialist_analysis(specialist_name: str, video_context: str) -> str:
    """Explain the analysis made by the specialist based on the video context."""
    key = _find_specialist_key(specialist_name)
    if not key:
        return f"Specialist '{specialist_name}' not found."
    
    specialist_prompt = _read_prompt_from_s3(key)
    
    explanation_prompt = f"""Based on this specialist prompt:
{specialist_prompt}

And this video context:
{video_context}

Explain what kind of analysis this specialist would provide and what insights they would focus on."""
    
    response = llm_light.invoke(explanation_prompt)
    return response.content


@tool
def consult_specialist(specialist_name: str, question: str, video_context: str) -> str:
    """Consult the specialist with the question provided."""
    key = _find_specialist_key(specialist_name)
    if not key:
        return f"Specialist '{specialist_name}' not found."
    
    specialist_prompt = _read_prompt_from_s3(key)
    
    full_prompt = f"""{specialist_prompt}

Video Context: {video_context}
Question: {question}

Provide a detailed analysis based on your expertise."""
    
    response = llm_light.invoke(full_prompt)
    return response.content


# -----------------------------------------------------------------------------
# New prompt creation
# -----------------------------------------------------------------------------

@tool
def create_prompt_for_other_topic(topic: str, details: str) -> str:
    """Create a specialist prompt for analyzing videos of any sport/topic."""
    creation_prompt = f"""Create a specialist prompt for analyzing {topic} videos.
Focus areas: {details}

Generate a comprehensive prompt that defines:
1. The specialist's expertise and role
2. Key aspects to analyze
3. Common errors to identify
4. Recommendations format"""
    
    response = llm_light.invoke(creation_prompt)
    return response.content


@tool
def create_specialist_prompt(specialist_name: str, question: str, video_context: str = "") -> str:
    """Create a prompt for a specific specialist using a random existing prompt as template."""
    specialists = _list_prompts_from_s3()
    template_content = ""
    
    if specialists:
        random_specialist = random.choice(specialists)
        key = _find_specialist_key(random_specialist)
        if key:
            template_content = _read_prompt_from_s3(key)
    
    creation_prompt = f"""Create a specialist prompt for: {specialist_name}

Template for inspiration:
{template_content}

Question to address: {question}
{f"Video context: {video_context}" if video_context else ""}

Generate a prompt with: expertise definition, analysis points, output format, and technical knowledge."""
    
    response = llm_light.invoke(creation_prompt)
    return response.content


@tool
def save_specialist_prompt(specialist_name: str, prompt_content: str) -> str:
    """Save the specialist prompt to the S3 bucket."""
    key = f"{PROMPTS_PREFIX}{specialist_name}.txt"
    try:
        s3_client.put_object(Bucket=BUCKET_NAME, Key=key, Body=prompt_content.encode("utf-8"))
        return f"Specialist prompt '{specialist_name}' saved successfully to S3."
    except Exception as e:
        return f"Error saving specialist prompt: {str(e)}"


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

# No checkpointer or store as requested
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
)


def call_agent(user_query: str, video_context_analysis: str = ""):
    # Stateless execution
    ai_response = react_agent.invoke(input=prompt_template.invoke({
        "video_context_analysis": video_context_analysis, "user_query": user_query
    }))['messages'][-1].content

    ai_response = re.sub(r'<thinking>.*?</thinking>', '', ai_response, flags=re.DOTALL).strip()
    
    return ai_response
