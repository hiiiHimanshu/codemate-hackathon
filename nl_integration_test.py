#!/usr/bin/env python3
"""
Integration test for NL parser functionality.
"""

from nl.parser import NLParser


def test_nl_parser():
    """Test NL parser functionality."""
    parser = NLParser()
    
    print("Testing NL Parser...")
    
    # Test create folder rule
    result = parser.parse("create a folder called test")
    print(f"'create a folder called test' -> {result}")
    assert result == ["mkdir test"]
    
    # Test move rule
    result = parser.parse("move file1 to folder1")
    print(f"'move file1 to folder1' -> {result}")
    assert result == ["mv file1 folder1/"]
    
    # Test list files rule
    result = parser.parse("list files")
    print(f"'list files' -> {result}")
    assert result == ["ls "]
    
    result = parser.parse("list files in /home")
    print(f"'list files in /home' -> {result}")
    assert result == ["ls /home"]
    
    # Test show file rule
    result = parser.parse("show file.txt")
    print(f"'show file.txt' -> {result}")
    assert result == ["cat file.txt"]
    
    # Test classification
    assert parser.classify_as_nl("create a folder called test")
    assert parser.classify_as_nl("move file1 to folder1")
    assert not parser.classify_as_nl("ls -la")
    assert not parser.classify_as_nl("cd /home")
    
    print("All NL parser tests passed!")


if __name__ == "__main__":
    test_nl_parser()
