from setuptools import setup, find_packages

setup(
    name="dcmtags-lyx",  # 套件名稱 (pip install dcmtags-lyx)
    version="0.0.2",     # 版本號
    author="Jocelyn",
    author_email="cindysa1107@gmail.com",
    description="A package for handling DICOM tag extraction and batch merging",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),   # 自動找到你寫的程式 (資料夾要有 __init__.py)
    install_requires=[
        "pandas",
        "pydicom",
        "tqdm",
        "XlsxWriter",
        "matplotlib",
        "openpyxl",      # 因為你要讀 Excel
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
