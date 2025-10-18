import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="goldenpotato888",
    version="0.1.3",
    packages=setuptools.find_packages(),

    author="Solomon Methvin",
    author_email="potatocubers@gmail.com",
    description="idk random stuff",
    long_description=long_description,
    long_description_content_type="text/markdown", # Specify the format of the long description
    url="https://github.com/GoldenPotato888/goldenpotato888-pythonpackage", # Project homepage or repository link
    license="MIT",
    
    install_requires=[
        'requests>=2.25.1',
        'google-api-python-client',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    include_package_data=True,
    python_requires='>=3.6',
)