from setuptools import setup, find_packages

setup(
    name="html2pdf_chromium",
    version="0.1.0",
    author="Vinicius Benevides",
    author_email="massaki1999@gmail.com",
    description="Convert HTML to PDF using Chromium browsers with zero Python dependencies",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VBenevides/html2pdf_chromium",  # Change this to your actual repo URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.7",
)
