from setuptools import setup, find_packages
setup(
    name="talkingdata",
    version="1.0.0",
    author="Mohammad Abdullah",
    author_email="mabdullaha407@gmail.com",
    description="A lightweight, multi-provider AI Data Analysis library using SQL reasoning on pandas DataFrames.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://mabdullah40.github.io/Open-Analysis/",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "duckdb",
        "html2text",
        "python-dotenv",
        "streamlit",
    ],
    extras_require={
        "groq": ["groq"],
        "gemini": ["google-genai"],
        "openai": ["openai"]
    }
)