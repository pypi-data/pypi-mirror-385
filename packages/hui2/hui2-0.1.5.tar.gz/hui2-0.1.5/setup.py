from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hui2",
    version="0.1.5",
    author="h1code2",
    author_email="h1code2@163.com",
    description="Android automation library with OCR support based on uiautomator2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/h1code2/hui2",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "uiautomator2>=3.4.1",
        "rapidocr-onnxruntime>=1.4.4",
        "loguru>=0.7.3",
        "opencv-python>=4.12.0.88",
    ],
    keywords="android automation ocr uiautomator2 testing",
)