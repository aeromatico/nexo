from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="nexo_core",
    version="0.1.0",
    description="Nexo ERP - Core Multi-tenant Module",
    author="Aero",
    author_email="admin@aero.bo",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
