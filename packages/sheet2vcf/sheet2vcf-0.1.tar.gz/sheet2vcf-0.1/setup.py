import setuptools

setuptools.setup(

    name= 'sheet2vcf',
    version= '0.1',
    author= 'Mohamed Elsayed',
    author_email="ms.moh.dev@gmail.com",
    url="https://github.com/MohamedElsayed-debug/sheet2vcf",
    description= 'Simple and efficient tool to export contact numbers from CSV sheets to VCF format',
    packages=setuptools.find_packages(),
    classifiers=[
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: MIT License"
    ],
    entry_points={'console_scripts': ['sheet2vcf=sheet2vcf.__main__:main',],},
)