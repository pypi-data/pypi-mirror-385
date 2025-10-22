from setuptools import setup, find_packages

setup(
    name="models_package_vasmoul",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=4.2",
    ],
    description="Django models for Project Management Dashboard",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Vasilis Moulopoulos",
    author_email="vmoulop@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
