from setuptools import setup, find_packages

setup(
    name="agentic_hr",
    version="0.1.0",
    description="Agentic HR: Production RAG pipeline for candidate-job matching using LLMs and LanceDB",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        # Optionally can parse requirements.txt
    ],
    include_package_data=True,
    python_requires=">=3.10",
)
