from setuptools import setup, find_packages

setup(
    name="sits-interval",
    version="0.1.0",
    license="MIT",
    description="Library for interval computation and Sentinel-2 cloud masking",
    author="Ashrith",
    packages=find_packages(),
    install_requires=["numpy", "datetime"],
    python_requires=">=3.8",
)
