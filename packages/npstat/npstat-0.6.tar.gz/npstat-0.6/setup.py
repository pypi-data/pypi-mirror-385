from setuptools import setup, find_packages

setup(
    name="npstat",
    version="0.6",
    author="EcoAI",
    description="Statistical hypothesis testing package",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "scipy",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "numpy"
    ],
    python_requires=">=3.6",

)







