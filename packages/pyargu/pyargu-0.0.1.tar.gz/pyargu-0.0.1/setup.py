from setuptools import setup, find_packages

setup(
    name="pyargu",
    version="0.0.1",
    author="Athallah Rajendra Putra Juniarto",
    author_email="example@email.com",
    description="Library parsing argumen command-line sederhana dari nol",
    packages=find_packages(),
    python_requires=">=3.7",
    license="MIT",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
        "Operating System :: OS Independent",
    ],
)
