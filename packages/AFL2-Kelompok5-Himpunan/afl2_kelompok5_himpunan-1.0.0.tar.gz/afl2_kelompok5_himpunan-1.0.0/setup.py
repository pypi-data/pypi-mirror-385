from setuptools import setup, find_packages

setup(
    name="AFL2_Kelompok5_Himpunan", 
    version="1.0.0",
    install_requires=[],
    author="Kelompok 5",
    author_email="vwijaya11@student.ciputra.ac.id, christianlaury01@student.ciputra.ac.id, rfebrian01@student.ciputra.ac.id",
    description="Mini Project II: Implementasi Himpunan dengan Bahasa Pemrogramman Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VivianWijaya06/Himpunan_Kelompok5",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Education",
    ],
    python_requires=">=3.6",
)