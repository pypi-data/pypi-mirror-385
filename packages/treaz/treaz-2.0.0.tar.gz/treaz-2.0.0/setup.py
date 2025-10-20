from setuptools import setup, find_packages

setup(
    name="treaz",
    version="2.0.0",
    description="Advanced system & network reconnaissance tool with hacker-style CLI interface",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="ervuln",
    license="Apache-2.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "psutil",
        "requests",
        "colorama",
        "shutilwhich; platform_system != 'Windows'",
        "wmi; platform_system == 'Windows'",
    ],
    keywords=["system", "recon", "network", "hacker", "terminal", "CLI", "cyber"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={
        "console_scripts": [
            "treaz=treaz:main",
        ],
    },
)
