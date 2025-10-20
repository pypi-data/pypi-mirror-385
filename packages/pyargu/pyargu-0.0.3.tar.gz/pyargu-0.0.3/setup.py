from setuptools import setup, find_packages

setup(
    name="pyargu",
    version="0.0.3",
    author="Athallah Rajendra Putra Juniarto",
    author_email="example@email.com",
    description="Parser argumen command-line dari nol: config, ENV, validator, dan completion",
    packages=find_packages(),
    python_requires=">=3.8",
    license="MIT",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
)
