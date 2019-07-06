import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='LambdaALBRouter',
    version='0.1',
    author="Jeordy Rebbereh",
    author_email="jeordy@gmail.com",
    description="A package with flask-like syntax for routing requests from an AWS ALB in Lambda",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JeordyR/LambdaALBRouter",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
