from setuptools import setup, find_packages

setup(
    name="neuron_assistant",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "llama-cpp-python",
        "huggingface-hub",
        "cryptography",
        "torch",
        "psutil",
    ],
    entry_points={
        "console_scripts": [
            "neuron=neuron_assistant.assistant:main",
        ],
    },
    include_package_data=True,
    description="Neuron AI assistant by Dev Patel",
    author="Dev Patel",
    python_requires=">=3.8",
)
