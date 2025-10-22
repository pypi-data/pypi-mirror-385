from setuptools import setup, find_packages

setup (
    
    name='ITL_service',
    version='1.3',
    packages=find_packages(),
    description="Libreria para control de dispositivo ITL NV4000 y SCS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Santiago Cuervo",
    author_email="santic9999@gmail.com",
    url="https://github.com/Santiago702/itl_service",
    install_requires=["requests"],  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6'
)
