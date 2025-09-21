"""
Unit tests for natural language parser.
"""

import unittest
from nl.parser import NLParser


class TestNLParser(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = NLParser()
        
    def test_classify_as_nl(self):
        """Test natural language classification."""
        # Test NL inputs
        self.assertTrue(self.parser.classify_as_nl("create a folder called test"))
        self.assertTrue(self.parser.classify_as_nl("list files in docs"))
        
        # Test command inputs
        self.assertFalse(self.parser.classify_as_nl("ls -l"))
        self.assertFalse(self.parser.classify_as_nl("pwd"))
        
    def test_parse_create_folder(self):
        """Test parsing create folder command."""
        result = self.parser.parse("create a folder called test")
        self.assertEqual(result, ["mkdir test"])
        
    def test_parse_move(self):
        """Test parsing move command."""
        result = self.parser.parse("move file.txt to docs")
        self.assertEqual(result, ["mv file.txt docs/"])
        
    def test_parse_list_files(self):
        """Test parsing list files command."""
        result = self.parser.parse("list files")
        self.assertEqual(result, ["ls "])
        
        result = self.parser.parse("list files in docs")
        self.assertEqual(result, ["ls docs"])
        
    def test_parse_show_file(self):
        """Test parsing show file command."""
        result = self.parser.parse("show README.md")
        self.assertEqual(result, ["cat README.md"])
        
    def test_parse_invalid(self):
        """Test parsing invalid input."""
        result = self.parser.parse("this is not a valid command")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()