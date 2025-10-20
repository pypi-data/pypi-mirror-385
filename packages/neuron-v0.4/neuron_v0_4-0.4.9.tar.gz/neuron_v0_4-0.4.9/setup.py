from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
README_FILE = Path(__file__).parent / "README.md"
long_description = ""
if README_FILE.exists():
    with open(README_FILE, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Neuron - A local AI assistant with advanced identity protection and hardware optimization"

# Read version from the main file
VERSION = "0.4.9"

# Core dependencies (always required)
CORE_REQUIREMENTS = [
    "torch>=2.0.0",
    "transformers>=4.30.0",
    "psutil>=5.9.0",
    "cryptography>=41.0.0",
]

# Optional dependencies for different use cases
EXTRA_REQUIREMENTS = {
    # For GPT4All support
    "gpt4all": [
        "gpt4all>=2.0.0",
    ],
    
    # For HuggingFace Hub features
    "huggingface": [
        "huggingface-hub>=0.16.0",
    ],
    
    # Development tools
    "dev": [
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.4.0",
        "isort>=5.12.0",
    ],
    
    # All optional features
    "all": [
        "gpt4all>=2.0.0",
        "huggingface-hub>=0.16.0",
    ],
}

setup(
    name="neuron_v0.4",  # Package name with version prefix
    version=VERSION,
    author="Dev Patel",
    author_email="devpatel@gmail.com",
    description="A local AI assistant with advanced identity protection and hardware optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devpatel/neuron-ai-assistant",  # Replace with actual URL
    project_urls={
        "Bug Tracker": "https://github.com/devpatel/neuron-ai-assistant/issues",
        "Documentation": "https://github.com/devpatel/neuron-ai-assistant/wiki",
        "Source Code": "https://github.com/devpatel/neuron-ai-assistant",
    },
    
    # Package configuration
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=CORE_REQUIREMENTS,
    extras_require=EXTRA_REQUIREMENTS,
    
    # Entry points for command-line scripts
    entry_points={
        "console_scripts": [
            "neuron=neuron_assistant.assistant:main",  # Points to assistant.py:main
            "neuron-v0.4=neuron_assistant.assistant:main",
        ],
    },
    
    # Package data to include
    package_data={
        "": [
            "*.json",
            "*.pem",
            "*.sig",
            "README.md",
            "LICENSE",
        ],
    },
    
    # Classification metadata
    classifiers=[
        # Development Status
        "Development Status :: 4 - Beta",
        
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        
        # Topic
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        
        # License
        "License :: OSI Approved :: MIT License",  # Adjust based on your license
        
        # Python versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        
        # OS
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        
        # Environment
        "Environment :: Console",
        "Environment :: GPU :: NVIDIA CUDA",
        
        # Natural Language
        "Natural Language :: English",
    ],
    
    # Keywords for PyPI search
    keywords=[
        "ai",
        "assistant",
        "chatbot",
        "llm",
        "language-model",
        "gpt4all",
        "mistral",
        "transformers",
        "local-ai",
        "privacy",
        "cuda",
        "pytorch",
    ],
    
    # License
    license="MIT",  # Adjust based on your license
    
    # Include additional files
    include_package_data=True,
    
    # Zip safety
    zip_safe=False,
)