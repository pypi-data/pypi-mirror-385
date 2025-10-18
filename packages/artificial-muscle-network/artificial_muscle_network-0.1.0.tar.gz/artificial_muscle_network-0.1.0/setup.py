from setuptools import setup, find_packages

setup(
    name="artificial-muscle-network",
    version="0.1.0",
    description="Artificial Muscle Network: physics-inspired optimization for scheduling, routing, and allocation",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="AMN Maintainers",
    license="MIT",
    python_requires=">=3.9",
    packages=find_packages(include=["amn", "amn.*"]),
    include_package_data=True,
    install_requires=[],  # zero runtime deps
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Homepage": "https://github.com/eldm-ethanmoore/artificial-muscle-network",
        "Documentation": "https://eldm-ethanmoore.github.io/artificial-muscle-network/",
        "Issues": "https://github.com/eldm-ethanmoore/artificial-muscle-network/issues",
    },
)
