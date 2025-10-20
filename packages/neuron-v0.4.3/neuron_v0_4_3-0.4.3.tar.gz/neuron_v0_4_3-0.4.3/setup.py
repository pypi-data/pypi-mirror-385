from setuptools import setup, find_packages
import os

# Get the absolute path of the directory containing setup.py
here = os.path.abspath(os.path.dirname(__file__))

# Read the README
try: 
    with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Neuron AI Assistant — auto GPU/CPU detection and local AI."

setup(
    name="neuron_v0.4.3",
    version="0.4.3",
    author="Dev Patel",
    author_email="devpatel2u@gmail.com",
    description="Neuron AI Assistant — auto GPU/CPU detection and local AI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/neuron-assistant",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "torch",
        "transformers",
        "huggingface-hub",
        "cryptography",
        "psutil",
        "gpt4all"
    ],
    entry_points={
        "console_scripts": [
            "Neuron=neuron_assistant.assistant:main"
        ]
    },
)
