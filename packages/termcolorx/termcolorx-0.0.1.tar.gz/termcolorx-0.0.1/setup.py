from setuptools import setup, find_packages

setup(
    name="termcolorx",
    version="0.0.1",
    author="ATHALLAH RAJENDRA PUTRA JUNIARTO",
    author_email="athallahwork50@gmail.com",
    description="Library pewarna teks terminal lengkap (ANSI, RGB, Gradien, Logger, Animasi) dari dasar.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Athallah1234/termcolorx",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Terminals",
        "Topic :: Utilities",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.13",
)
