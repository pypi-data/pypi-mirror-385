from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README if available
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="NeuraPython",
    version="2.0.4",
    author="Ibrahim Shahid",
    author_email="ibrahimshahid7767@gmail.com",
    description=(
        "NeuraPython is a unified framework combining AI, Machine Learning, "
        "Data Science, Web Development, Scientific Computation, and Utility tools."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IbrahimShahid7767/neurapython",
    project_urls={
        "Bug Tracker": "https://github.com/IbrahimShahid7767/neurapython/issues",
        "Documentation": "https://pypi.org/project/NeuraPython/",
    },
    packages=find_packages(include=["neurapython", "neurapython.*"]),
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "pygame",
        "opencv-python",
        "pyttsx3",
        "speechrecognition",
        "flask",
        "scikit-learn",
        "pdfplumber",
        "pdf2docx",
        "docx2pdf",
        "fpdf",
        "markdown",
        "beautifulsoup4",
        "sympy",
        "tensorflow",
        "torch",
        "joblib",
        "qrcode",
        "requests",
        "pillow",
    ],
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries",
    ],
    keywords=[
        "AI", "Machine Learning", "Deep Learning", "Data Science",
        "Physics", "Chemistry", "Math", "Flask", "Neural Network",
        "Utility", "Automation", "Computation"
    ],
)
