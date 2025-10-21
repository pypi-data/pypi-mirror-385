# This makes the directory a package. 
# You can use it to define what gets exposed when someone imports the package.
# src/your_package_name/__init__.py

from duderanch_package.firstModule import hello

__all__ = ["hello"]

#This allows people to do:
# from your_package_name import hello

# print(hello())         # "Hello, World!"
# print(hello("Alice"))  # "Hello, Alice!"
