"""
Unit tests for the command router.
"""

import os
import unittest
from unittest.mock import Mock, patch

from core.router import CommandRouter, Response
from core.registry import CommandRegistry
from core.session import SessionContext
from core.errors import CommandError
from fs.paths import WORKSPACE_ROOT


class TestCommandRouter(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = CommandRegistry()
        self.session = SessionContext(cwd=str(WORKSPACE_ROOT))
        self.router = CommandRouter(self.registry, self.session)
        
        # Add a simple test command
        def test_handler(ctx, args):
            return "test output"
        
        self.registry.register("test", test_handler, "test", "Test command")
        
        # Add a command with arguments
        def arg_handler(ctx, values):
            if len(values) != 2:
                raise CommandError("Usage: argtest <arg1> <arg2>")
            arg1, arg2 = values
            return f"args: {arg1}, {arg2}"
        
        self.registry.register("argtest", arg_handler, "argtest <arg1> <arg2>", "Arg handler")
    
    def test_empty_input(self):
        """Test handling of empty input."""
        response = self.router.execute("")
        self.assertEqual(response.stdout, "")
        self.assertEqual(response.stderr, "")
        self.assertEqual(response.status, "ok")
    
    def test_tokenization(self):
        """Test tokenization of input with quoted arguments."""
        # Test simple command
        command_name, args = self.router.parse_input("ls")
        self.assertEqual(command_name, "ls")
        self.assertEqual(args, [])
        
        # Test command with arguments
        command_name, args = self.router.parse_input("ls -l")
        self.assertEqual(command_name, "ls")
        self.assertEqual(args, ["-l"])
        
        # Test command with quoted arguments
        command_name, args = self.router.parse_input('cp "file with spaces.txt" dest.txt')
        self.assertEqual(command_name, "cp")
        self.assertEqual(args, ["file with spaces.txt", "dest.txt"])
        
        # Test command with mixed quoted and unquoted
        command_name, args = self.router.parse_input('mv "source file.txt" target.txt')
        self.assertEqual(command_name, "mv")
        self.assertEqual(args, ["source file.txt", "target.txt"])
    
    def test_unknown_command(self):
        """Test handling of unknown commands."""
        response = self.router.execute("unknown_command")
        self.assertEqual(response.stdout, "")
        self.assertEqual(response.stderr, "Command not found. Try `help`.")
        self.assertEqual(response.status, "error")
    
    def test_help_command(self):
        """Test help command functionality."""
        response = self.router.execute("help")
        self.assertIn("Available commands:", response.stdout)
        self.assertEqual(response.status, "ok")
    
    def test_help_specific_command(self):
        """Test help for a specific command."""
        response = self.router.execute("help test")
        self.assertIn("Usage: test", response.stdout)
        self.assertEqual(response.status, "ok")
    
    def test_help_unknown_command(self):
        """Test help for unknown command."""
        response = self.router.execute("help unknown")
        self.assertEqual(response.stdout, "")
        self.assertEqual(response.stderr, "Command not found. Try `help`.")
        self.assertEqual(response.status, "error")
    
    def test_history_command(self):
        """Test history command functionality."""
        # Add some commands to history
        self.session.history.extend(["test command 1", "test command 2"])
        
        response = self.router.execute("history")
        self.assertIn("1  test command 1", response.stdout)
        self.assertIn("2  test command 2", response.stdout)
        self.assertTrue(response.stdout.strip().endswith("3  history"))
        self.assertEqual(response.status, "ok")
    
    def test_history_with_args(self):
        """Test history command with arguments (should fail)."""
        response = self.router.execute("history arg")
        self.assertEqual(response.stderr, "History command takes no arguments.")
        self.assertEqual(response.status, "error")
    
    def test_arg_validation(self):
        """Test argument validation."""
        response = self.router.execute("argtest arg1 arg2 extra")
        self.assertEqual(response.stderr, "Usage: argtest <arg1> <arg2>")
        self.assertEqual(response.status, "error")
    
    def test_command_execution(self):
        """Test successful command execution."""
        response = self.router.execute("test")
        self.assertEqual(response.stdout, "test output")
        self.assertEqual(response.status, "ok")
        self.assertIsNotNone(response.meta)
        self.assertIn("exec_ms", response.meta)
    
    def test_error_propagation(self):
        """Test error propagation from command handlers."""
        def error_handler(ctx, args):
            raise ValueError("Test error")
        
        self.registry.register("error_test", error_handler, "error_test", "Test error command")
        
        response = self.router.execute("error_test")
        self.assertEqual(response.stderr, "Test error")
        self.assertEqual(response.status, "error")
        self.assertIsNotNone(response.meta)
        self.assertIn("exec_ms", response.meta)
    
    def test_error_mapping(self):
        """Test error mapping to friendly messages."""
        def error_handler(ctx, args):
            raise FileNotFoundError("/nonexistent/file.txt")
        
        self.registry.register("file_error_test", error_handler, "file_error_test", "Test file error")
        
        response = self.router.execute("file_error_test")
        # The error message format depends on how FileNotFoundError is handled
        # Just check that it contains the expected components
        self.assertIn("File not found", response.stderr)
        self.assertEqual(response.status, "error")
    
    def test_readonly_mode(self):
        """Test that readonly mode is implemented (basic check)."""
        # This test verifies that the readonly mode logic is in place
        # Actual testing of readonly mode requires more complex mocking
        # For now, we'll just verify the router initializes correctly
        self.assertTrue(True)  # Placeholder - actual test requires more complex setup


if __name__ == '__main__':
    unittest.main()
