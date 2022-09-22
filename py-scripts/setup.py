from setuptools import setup, find_packages

setup(
    name="toolbelt",
    version="0.1.0",
    description="K8s toolbelt",
    author="Planetarium",
    author_email="engineering@planetariumhq.com",
    packages=find_packages(
        where=".",
        include=["toolbelt*"],
        exclude=["tests"],
    ),
    python_requires=">=3.6",
    install_requires=[
        "py7zr~=0.20.0",
        "structlog>=16.1,<22.1",
        "boto3~=1.24",
        "PyYAML==6.0",
        "requests==2.26.0",
        "kubernetes~=24.2",
        "typer[all]~=0.6.1",
        "python-dotenv~=0.19",
        "slack_sdk>=3.12,<3.19",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
