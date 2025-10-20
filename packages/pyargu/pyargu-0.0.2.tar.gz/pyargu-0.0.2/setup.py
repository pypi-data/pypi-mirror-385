from setuptools import setup, find_packages

setup(
    name="pyargu",
    version="0.0.2",
    author="Athallah Rajendra Putra Juniarto",
    author_email="example@email.com",
    description="Library parsing argumen command-line buatan sendiri dari nol (super lengkap)",
    packages=find_packages(),
    python_requires=">=3.8",
    license="MIT",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
        "Operating System :: OS Independent",
    ],
)