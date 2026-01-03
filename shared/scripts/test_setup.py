#!/usr/bin/env python3
"""
LiteLLM + Langfuse Stack Health Check

Run this script to verify your deployment is working correctly.

Usage:
    export LITELLM_URL=https://your-litellm.up.railway.app
    export LITELLM_API_KEY=sk-your-key
    export LANGFUSE_URL=https://your-langfuse.up.railway.app
    
    python test_setup.py
"""

import os
import sys
import requests
from typing import Tuple, Optional


def check_env_vars() -> Tuple[bool, list]:
    """Check required environment variables."""
    required = ["LITELLM_URL", "LITELLM_API_KEY"]
    optional = ["LANGFUSE_URL"]
    
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        return False, missing
    return True, []


def check_litellm_health(url: str) -> Tuple[bool, str]:
    """Check LiteLLM health endpoint."""
    try:
        response = requests.get(f"{url}/health", timeout=10)
        if response.ok:
            return True, "LiteLLM is healthy"
        return False, f"LiteLLM returned status {response.status_code}"
    except requests.RequestException as e:
        return False, f"Cannot reach LiteLLM: {e}"


def check_litellm_models(url: str, api_key: str) -> Tuple[bool, str]:
    """Check if LiteLLM has models configured."""
    try:
        response = requests.get(
            f"{url}/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if response.ok:
            data = response.json()
            models = data.get("data", [])
            if models:
                model_names = [m.get("id", "unknown") for m in models[:5]]
                return True, f"Found {len(models)} models: {', '.join(model_names)}"
            return False, "No models configured in LiteLLM"
        return False, f"Models endpoint returned {response.status_code}"
    except requests.RequestException as e:
        return False, f"Cannot fetch models: {e}"


def check_litellm_completion(url: str, api_key: str) -> Tuple[bool, str]:
    """Test a simple completion (requires at least one model configured)."""
    try:
        # First get available models
        models_resp = requests.get(
            f"{url}/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        
        if not models_resp.ok:
            return False, "Cannot fetch models to test"
        
        models = models_resp.json().get("data", [])
        if not models:
            return False, "No models available for testing"
        
        model_name = models[0].get("id", "gpt-4o")
        
        # Try a completion
        response = requests.post(
            f"{url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model_name,
                "messages": [{"role": "user", "content": "Say 'test successful' and nothing else."}],
                "max_tokens": 20
            },
            timeout=30
        )
        
        if response.ok:
            content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            return True, f"Completion successful with {model_name}: {content[:50]}"
        
        error = response.json().get("error", {}).get("message", response.text[:100])
        return False, f"Completion failed: {error}"
        
    except requests.RequestException as e:
        return False, f"Completion request failed: {e}"


def check_langfuse_health(url: str) -> Tuple[bool, str]:
    """Check Langfuse health endpoint."""
    if not url:
        return True, "Langfuse URL not provided (optional)"
    
    try:
        response = requests.get(f"{url}/api/public/health", timeout=10)
        if response.ok:
            return True, "Langfuse is healthy"
        return False, f"Langfuse returned status {response.status_code}"
    except requests.RequestException as e:
        return False, f"Cannot reach Langfuse: {e}"


def print_result(name: str, success: bool, message: str):
    """Print a formatted result."""
    icon = "✅" if success else "❌"
    print(f"{icon} {name}")
    print(f"   {message}")
    print()


def main():
    print("=" * 60)
    print("🔍 LiteLLM + Langfuse Stack Health Check")
    print("=" * 60)
    print()
    
    # Check environment variables
    env_ok, missing = check_env_vars()
    if not env_ok:
        print_result(
            "Environment Variables",
            False,
            f"Missing required variables: {', '.join(missing)}"
        )
        print("\nSet the required variables:")
        print("  export LITELLM_URL=https://your-litellm.up.railway.app")
        print("  export LITELLM_API_KEY=sk-your-key")
        print("  export LANGFUSE_URL=https://your-langfuse.up.railway.app  # optional")
        sys.exit(1)
    
    print_result("Environment Variables", True, "All required variables set")
    
    # Get URLs
    litellm_url = os.getenv("LITELLM_URL").rstrip("/")
    litellm_key = os.getenv("LITELLM_API_KEY")
    langfuse_url = os.getenv("LANGFUSE_URL", "").rstrip("/")
    
    all_passed = True
    
    # Check LiteLLM health
    ok, msg = check_litellm_health(litellm_url)
    print_result("LiteLLM Health", ok, msg)
    all_passed = all_passed and ok
    
    # Check LiteLLM models
    ok, msg = check_litellm_models(litellm_url, litellm_key)
    print_result("LiteLLM Models", ok, msg)
    if not ok:
        print("   💡 Add models via LiteLLM UI or API:")
        print(f"      {litellm_url}/ui")
        print()
    all_passed = all_passed and ok
    
    # Check completion (only if models exist)
    if "Found" in msg:  # Models were found
        ok, msg = check_litellm_completion(litellm_url, litellm_key)
        print_result("LiteLLM Completion", ok, msg)
        all_passed = all_passed and ok
    
    # Check Langfuse
    ok, msg = check_langfuse_health(langfuse_url)
    print_result("Langfuse Health", ok, msg)
    if langfuse_url:
        all_passed = all_passed and ok
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("🎉 All checks passed! Your stack is ready.")
        print()
        print("Next steps:")
        print(f"  1. Access LiteLLM UI: {litellm_url}/ui")
        if langfuse_url:
            print(f"  2. Access Langfuse UI: {langfuse_url}")
        print("  3. Make API calls and check traces in Langfuse")
    else:
        print("⚠️  Some checks failed. Review the issues above.")
        sys.exit(1)
    
    print("=" * 60)


if __name__ == "__main__":
    main()
