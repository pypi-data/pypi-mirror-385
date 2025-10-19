#!/usr/bin/env python3
"""
Script to download and run efficient models from Ollama using MCLI model service.

This script uses the Ollama API to pull the most efficient models and then
integrates them with the MCLI model service for local inference.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import click
import requests

# Add the parent directory to the path so we can import the model service
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mcli.workflow.model_service.model_service import ModelManager, ModelService

# Efficient models from Ollama with their model names
EFFICIENT_MODELS = {
    "phi3-mini": {
        "name": "Phi-3 Mini",
        "ollama_name": "phi3-mini",
        "description": "Microsoft's lightweight 3.8B model with excellent reasoning",
        "parameters": "3.8B",
        "efficiency_score": 9.5,
        "accuracy_score": 8.5,
        "tags": ["reasoning", "efficient", "lightweight"],
    },
    "gemma3n-1b": {
        "name": "Gemma3n 1B",
        "ollama_name": "gemma3n:1b",
        "description": "Google's efficient 1B model for everyday devices",
        "parameters": "1B",
        "efficiency_score": 9.8,
        "accuracy_score": 7.5,
        "tags": ["efficient", "small", "fast"],
    },
    "tinyllama-1.1b": {
        "name": "TinyLlama 1.1B",
        "ollama_name": "tinyllama:1.1b",
        "description": "Compact 1.1B model trained on 3 trillion tokens",
        "parameters": "1.1B",
        "efficiency_score": 9.7,
        "accuracy_score": 7.0,
        "tags": ["compact", "fast", "lightweight"],
    },
    "phi4-mini-reasoning": {
        "name": "Phi-4 Mini Reasoning",
        "ollama_name": "phi4-mini-reasoning",
        "description": "Lightweight 3.8B model with advanced reasoning",
        "parameters": "3.8B",
        "efficiency_score": 9.3,
        "accuracy_score": 8.8,
        "tags": ["reasoning", "advanced", "efficient"],
    },
    "llama3.2-1b": {
        "name": "Llama 3.2 1B",
        "ollama_name": "llama3.2:1b",
        "description": "Meta's efficient 1B model with good performance",
        "parameters": "1B",
        "efficiency_score": 9.6,
        "accuracy_score": 7.8,
        "tags": ["meta", "efficient", "balanced"],
    },
}


def check_ollama_installed():
    """Check if Ollama is installed and running"""
    try:
        # Check if ollama command exists
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Ollama found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama command failed")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found. Please install Ollama first:")
        print("   Visit: https://ollama.com/download")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Ollama command timed out")
        return False


def check_ollama_server():
    """Check if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server is running")
            return True
        else:
            print("❌ Ollama server not responding")
            return False
    except requests.exceptions.RequestException:
        print("❌ Ollama server not running. Starting Ollama...")
        try:
            subprocess.Popen(
                ["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            time.sleep(3)
            return check_ollama_server()
        except Exception as e:
            print(f"❌ Failed to start Ollama server: {e}")
            return False


def get_system_info():
    """Get system information for model selection"""
    import psutil

    # Get CPU info
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    memory_gb = psutil.virtual_memory().total / (1024**3)

    # Check for GPU
    try:
        import torch

        gpu_available = torch.cuda.is_available()
        if gpu_available:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        else:
            gpu_name = "None"
            gpu_memory = 0
    except ImportError:
        gpu_available = False
        gpu_name = "PyTorch not available"
        gpu_memory = 0

    return {
        "cpu_count": cpu_count,
        "cpu_freq_mhz": cpu_freq.current if cpu_freq else 0,
        "memory_gb": memory_gb,
        "gpu_available": gpu_available,
        "gpu_name": gpu_name,
        "gpu_memory_gb": gpu_memory,
    }


def recommend_model(system_info: Dict) -> str:
    """Recommend the best model based on system capabilities"""
    print("🔍 Analyzing system capabilities...")
    print(f"  CPU Cores: {system_info['cpu_count']}")
    print(f"  CPU Frequency: {system_info['cpu_freq_mhz']:.0f} MHz")
    print(f"  RAM: {system_info['memory_gb']:.1f} GB")
    print(f"  GPU: {system_info['gpu_name']}")
    print(f"  GPU Memory: {system_info['gpu_memory_gb']:.1f} GB")

    # Recommendation logic based on system capabilities
    if system_info["gpu_available"] and system_info["gpu_memory_gb"] >= 4:
        # Good GPU available
        if system_info["memory_gb"] >= 16:
            return "phi3-mini"  # Best balance for good hardware
        else:
            return "gemma3n-1b"  # More memory efficient
    elif system_info["memory_gb"] >= 8:
        # CPU-only with decent RAM
        return "phi3-mini"
    else:
        # Limited resources
        return "tinyllama-1.1b"


def pull_ollama_model(model_key: str) -> bool:
    """Pull a model from Ollama"""
    model_info = EFFICIENT_MODELS[model_key]

    print(f"\n📥 Pulling {model_info['name']} from Ollama...")
    print(f"  Model: {model_info['ollama_name']}")
    print(f"  Parameters: {model_info['parameters']}")
    print(f"  Efficiency Score: {model_info['efficiency_score']}/10")
    print(f"  Accuracy Score: {model_info['accuracy_score']}/10")

    try:
        # Pull the model using ollama command
        result = subprocess.run(
            ["ollama", "pull", model_info["ollama_name"]],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
        )

        if result.returncode == 0:
            print(f"✅ Successfully pulled {model_info['name']}")
            return True
        else:
            print(f"❌ Failed to pull {model_info['name']}: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"❌ Timeout while pulling {model_info['name']}")
        return False
    except Exception as e:
        print(f"❌ Error pulling {model_info['name']}: {e}")
        return False


def test_ollama_model(model_key: str):
    """Test the Ollama model with sample prompts"""
    model_info = EFFICIENT_MODELS[model_key]

    print(f"\n🧪 Testing {model_info['name']} via Ollama...")

    test_prompts = [
        "Explain quantum computing in simple terms.",
        "Write a Python function to calculate fibonacci numbers.",
        "What are the benefits of renewable energy?",
        "Translate 'Hello, how are you?' to Spanish.",
    ]

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Test {i}: {prompt}")

        try:
            # Use Ollama API to generate response
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model_info["ollama_name"], "prompt": prompt, "stream": False},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                print(f"⏱️  Response time: {result.get('eval_duration', 0):.2f} seconds")
                print(
                    f"🤖 Response: {response_text[:200]}{'...' if len(response_text) > 200 else ''}"
                )
            else:
                print(f"❌ API error: {response.status_code}")

        except Exception as e:
            print(f"❌ Error generating response: {e}")


def list_available_models():
    """List models available in Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("\n📋 Available models in Ollama:")
            for model in models:
                print(f"  - {model['name']} ({model.get('size', 'unknown size')})")
            return models
        else:
            print("❌ Failed to get model list")
            return []
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []


def create_mcli_integration_script(model_key: str):
    """Create a script to integrate the Ollama model with MCLI"""
    model_info = EFFICIENT_MODELS[model_key]

    script_content = f'''#!/usr/bin/env python3
"""
Integration script for {model_info['name']} with MCLI model service.
This script provides a bridge between Ollama and MCLI model service.
"""

import requests
import json
import time
from typing import Dict, Any

class OllamaMCLIBridge:
    def __init__(self, ollama_model: str, mcli_api_url: str = "http://localhost:8000"):
        self.ollama_model = ollama_model
        self.mcli_api_url = mcli_api_url
        
    def generate_text(self, prompt: str, max_length: int = 512, temperature: float = 0.7) -> str:
        """Generate text using Ollama model"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={{
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {{
                        "num_predict": max_length,
                        "temperature": temperature
                    }}
                }},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                raise Exception(f"Ollama API error: {{response.status_code}}")
                
        except Exception as e:
            raise Exception(f"Error generating text: {{e}}")
    
    def test_model(self):
        """Test the model with sample prompts"""
        test_prompts = [
            "Explain quantum computing in simple terms.",
            "Write a Python function to calculate fibonacci numbers.",
            "What are the benefits of renewable energy?"
        ]
        
        print(f"🧪 Testing {{self.ollama_model}}...")
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\\n📝 Test {{i}}: {{prompt}}")
            
            try:
                start_time = time.time()
                response = self.generate_text(prompt)
                execution_time = time.time() - start_time
                
                print(f"⏱️  Response time: {{execution_time:.2f}} seconds")
                print(f"🤖 Response: {{response[:200]}}{{'...' if len(response) > 200 else ''}}")
                
            except Exception as e:
                print(f"❌ Error: {{e}}")

if __name__ == "__main__":
    bridge = OllamaMCLIBridge("{model_info['ollama_name']}")
    bridge.test_model()
'''

    script_path = Path(f"ollama_{model_key}_bridge.py")
    with open(script_path, "w") as f:
        f.write(script_content)

    # Make executable
    script_path.chmod(0o755)

    print(f"✅ Created integration script: {script_path}")
    return script_path


@click.command()
@click.option(
    "--model",
    type=click.Choice(list(EFFICIENT_MODELS.keys())),
    help="Specific model to download and run",
)
@click.option(
    "--auto", is_flag=True, default=True, help="Automatically select best model for your system"
)
@click.option("--test", is_flag=True, default=True, help="Run test prompts after setup")
@click.option("--list-models", is_flag=True, help="List available models in Ollama")
@click.option("--create-bridge", is_flag=True, help="Create MCLI integration script")
def main(model: Optional[str], auto: bool, test: bool, list_models: bool, create_bridge: bool):
    """Download and run efficient models from Ollama"""

    print("🚀 Ollama Efficient Model Runner")
    print("=" * 50)

    # Check Ollama installation
    if not check_ollama_installed():
        return 1

    # Check Ollama server
    if not check_ollama_server():
        return 1

    if list_models:
        list_available_models()
        return 0

    # Get system info and recommend model
    system_info = get_system_info()

    if model:
        selected_model = model
        print(f"🎯 Using specified model: {selected_model}")
    elif auto:
        selected_model = recommend_model(system_info)
        print(f"🎯 Recommended model: {selected_model}")
    else:
        print("Available models:")
        for key, info in EFFICIENT_MODELS.items():
            print(f"  {key}: {info['name']} ({info['parameters']})")
        selected_model = click.prompt(
            "Select model", type=click.Choice(list(EFFICIENT_MODELS.keys()))
        )

    # Pull the model
    if not pull_ollama_model(selected_model):
        print("❌ Failed to pull model")
        return 1

    # Test the model
    if test:
        test_ollama_model(selected_model)

    # Create integration script
    if create_bridge:
        script_path = create_mcli_integration_script(selected_model)
        print(f"\n🔗 Integration script created: {script_path}")
        print(f"   Run: python {script_path}")

    model_info = EFFICIENT_MODELS[selected_model]
    print(f"\n🎉 Setup complete! Model {model_info['name']} is ready to use.")
    print(f"📊 Model: {model_info['ollama_name']}")
    print(f"🌐 Ollama API: http://localhost:11434")
    print(f"📝 Use 'ollama list' to see all models")

    return 0


if __name__ == "__main__":
    sys.exit(main())
