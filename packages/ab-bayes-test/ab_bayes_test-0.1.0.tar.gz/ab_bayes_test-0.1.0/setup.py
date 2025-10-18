from setuptools import setup, find_packages

setup(
    name="ab_bayes_test",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24",
        "scipy>=1.10",
        "pandas>=2.1"
    ],
    python_requires=">=3.10",
    description="Bayesian A/B Testing for proportions and means",
    author="Thiago Guimarães",
    author_email="thiago.guimaraes.sto@gmail.com",
    url="https://github.com/thiagogsdsa/ab_bayes_test",
    project_urls={
        "LinkedIn": "https://www.linkedin.com/in/thiagogsdsa",
        "GitHub": "https://github.com/thiagogsdsa/ab_bayes_test"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
