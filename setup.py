from setuptools import setup, find_packages

setup(
  name='mp2c',
  version='0.0.1',  # You should change this to your actual version
  description='A Python package that convert MiniPascal code to C code',
  packages=find_packages(),  # Automatically finds sub-packages
  include_package_data=True,  # Includes data files in sub-packages
  install_requires=[
    # Add any external libraries your package depends on here
  ],
)
