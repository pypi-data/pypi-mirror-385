import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sheet2vcf",
    version="0.2",
    author="Mohamed Elsayed",
    author_email="ms.moh.dev@gmail.com",
    description="Simple and efficient tool to export contact numbers from CSV sheets to VCF format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MohamedElsayed-debug/sheet2vcf",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    entry_points={
        'console_scripts': [
            'sheet2vcf=sheet2vcf.__main__:main',
        ],
    },
)
