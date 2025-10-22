from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="manim-fa-physics",
    version="0.1.0",
    author="Tabesh Alli",
    description="افزونه فیزیک برای Manim (مکانیک، گرانش، اوپتیک، الکترومغناطیس، الکترواستاتیک)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tabesh2020/manim-fa-physics",
    packages=find_packages(),
    include_package_data=True,  # ← اضافه شد
    install_requires=["manim>=0.19.0", "numpy>=1.24"],
    python_requires=">=3.10",
    license="MIT",  # ← اختیاری ولی توصیه‌شده
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
