"""
LiteLLM + Langfuse Integration Examples

This file demonstrates how to use the LiteLLM gateway with automatic Langfuse tracing.
"""

import os
from openai import OpenAI


# ============================================================================
# Configuration
# ============================================================================

LITELLM_URL = os.getenv("LITELLM_URL", "https://your-litellm.up.railway.app")
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY", "sk-your-master-key")

# Initialize OpenAI client pointing to LiteLLM
client = OpenAI(
    api_key=LITELLM_API_KEY,
    base_url=LITELLM_URL
)


# ============================================================================
# Basic Usage
# ============================================================================

def basic_completion():
    """Simple chat completion - automatically traced in Langfuse."""
    response = client.chat.completions.create(
        model="gpt-4o",  # Use any model you've configured in LiteLLM
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]
    )
    return response.choices[0].message.content


def streaming_completion():
    """Streaming completion - also traced in Langfuse."""
    stream = client.chat.completions.create(
        model="claude-sonnet",
        messages=[
            {"role": "user", "content": "Write a haiku about programming."}
        ],
        stream=True
    )
    
    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            full_response += content
    
    print()  # Newline after streaming
    return full_response


# ============================================================================
# Advanced: Custom Trace Metadata
# ============================================================================

def completion_with_metadata():
    """
    Add custom metadata to traces for better filtering in Langfuse.
    
    LiteLLM forwards metadata to Langfuse automatically.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "Summarize this: AI is transforming industries."}
        ],
        extra_body={
            "metadata": {
                # These appear in Langfuse traces
                "user_id": "user-123",
                "session_id": "session-abc",
                "environment": "production",
                "feature": "summarization",
                "tags": ["summary", "demo"]
            }
        }
    )
    return response.choices[0].message.content


# ============================================================================
# Using Virtual Keys (for multi-tenant setups)
# ============================================================================

def create_virtual_key():
    """
    Create a virtual key with budget limits.
    
    Virtual keys let you:
    - Set spending limits per team/project
    - Restrict access to specific models
    - Track usage separately
    """
    import requests
    
    response = requests.post(
        f"{LITELLM_URL}/key/generate",
        headers={
            "Authorization": f"Bearer {LITELLM_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "models": ["gpt-4o", "claude-sonnet"],
            "max_budget": 50.0,  # $50 budget
            "budget_duration": "1mo",  # Monthly reset
            "metadata": {
                "team": "engineering",
                "project": "chatbot-v2"
            },
            "key_alias": "eng-team-key"
        }
    )
    
    if response.ok:
        data = response.json()
        print(f"Created key: {data['key']}")
        print(f"Expires: {data.get('expires')}")
        return data['key']
    else:
        print(f"Error: {response.text}")
        return None


def use_virtual_key(virtual_key: str):
    """Use a virtual key instead of master key."""
    virtual_client = OpenAI(
        api_key=virtual_key,
        base_url=LITELLM_URL
    )
    
    response = virtual_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    return response.choices[0].message.content


# ============================================================================
# Model Fallbacks
# ============================================================================

def completion_with_fallback():
    """
    LiteLLM automatically handles fallbacks if configured.
    
    Configure fallbacks in LiteLLM:
    - Via UI: Model Management → Fallbacks
    - Via API or config.yaml
    """
    # If gpt-4o fails, LiteLLM can automatically try claude-sonnet
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Test fallback"}],
        extra_body={
            "fallbacks": ["claude-sonnet", "gemini-pro"]  # Override default fallbacks
        }
    )
    return response.choices[0].message.content


# ============================================================================
# Function Calling / Tools
# ============================================================================

def function_calling_example():
    """Function calling works transparently through LiteLLM."""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city name"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "What's the weather in Paris?"}],
        tools=tools,
        tool_choice="auto"
    )
    
    return response.choices[0].message


# ============================================================================
# Embeddings
# ============================================================================

def get_embeddings():
    """Generate embeddings through LiteLLM."""
    response = client.embeddings.create(
        model="text-embedding-3-small",  # Configure this in LiteLLM
        input=["Hello world", "Goodbye world"]
    )
    return response.data[0].embedding[:5]  # First 5 dimensions


# ============================================================================
# Langfuse Direct Integration (for prompt management)
# ============================================================================

def use_langfuse_prompts():
    """
    Fetch prompts from Langfuse for prompt management.
    
    This requires direct Langfuse SDK connection.
    """
    from langfuse import Langfuse
    
    LANGFUSE_URL = os.getenv("LANGFUSE_URL", "https://your-langfuse.up.railway.app")
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    
    langfuse = Langfuse(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANGFUSE_URL
    )
    
    # Get a prompt template (create it first in Langfuse UI)
    try:
        prompt = langfuse.get_prompt("summarization-prompt")
        compiled = prompt.compile(text="Some text to summarize")
        
        # Use the compiled prompt with LiteLLM
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": compiled}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Prompt not found: {e}")
        return None


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LiteLLM + Langfuse Integration Demo")
    print("=" * 60)
    
    print("\n1. Basic Completion:")
    print("-" * 40)
    try:
        result = basic_completion()
        print(f"Response: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. Streaming Completion:")
    print("-" * 40)
    try:
        streaming_completion()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n3. Completion with Metadata:")
    print("-" * 40)
    try:
        result = completion_with_metadata()
        print(f"Response: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Check Langfuse UI to see all traces!")
    print("=" * 60)
