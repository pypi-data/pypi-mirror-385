from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="barnyard",
    version="2.0.0",
    description="Temporary Delete System for Safe Batch Automation and Lead Distribution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Henry",
    author_email="osas2henry@gmail.com",
    license="MIT",
    packages=find_packages(),  # remove the 'where' argument
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords="automation batch processing deletion safety recovery leads",
    include_package_data=True,
    install_requires=[],
)
