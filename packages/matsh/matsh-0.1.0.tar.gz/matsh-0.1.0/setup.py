from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="matsh",
    version="0.1.0",
    author="Your Name",  # Замените на свое имя
    author_email="your.email@example.com",  # Замените на свою почту
    description="Python library for DeepSeek AI models via OpenRouter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "openai>=1.0.0",
    ],
    keywords="ai, deepseek, openrouter, chatbot",
    url="https://github.com/yourusername/matsh",  # Замените на свой репозиторий
)