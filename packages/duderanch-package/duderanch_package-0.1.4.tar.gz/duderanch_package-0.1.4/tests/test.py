# tests/test_your_module.py

import unittest
from duderanch_package import hello

class TestHelloFunction(unittest.TestCase):
    def test_hello_default(self):
        self.assertEqual(hello(), "Hello, World!")

    def test_hello_custom_name(self):
        self.assertEqual(hello("Alice"), "Hello, Alice!")

if __name__ == "__main__":
    unittest.main()
