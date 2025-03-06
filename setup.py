from setuptools import setup, find_packages

setup(
    name="wawachat",
    version="1.5.0",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "huggingface-hub>=0.16.0",
        "python-dotenv>=0.19.0",
    ],
    author="Wagner Silva Montes",
    author_email="your.email@example.com",
    description="A lightweight chat application powered by TinyLlama",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/WawaChat",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "wawachat=WawaChat.wawachat-v1:main",
        ],
    },
)
