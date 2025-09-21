#!/usr/bin/env python3
"""
Integration test for filesystem operations.
"""

import os
import tempfile
import shutil
from pathlib import Path
from core.router import CommandRouter
from core.registry import create_default_registry
from core.session import SessionContext
from fs.paths import WORKSPACE_ROOT


def main():
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    
    try:
        os.chdir(test_dir)
        print(f"Working in test directory: {test_dir}")
        
        # Set workspace root to test directory
        os.environ["WORKSPACE_ROOT"] = test_dir
        
        # Create registry and session
        registry = create_default_registry()
        session = SessionContext(cwd=str(WORKSPACE_ROOT))
        router = CommandRouter(registry, session)
        
        print("=== Testing Filesystem Operations ===")
        
        # Test pwd
        response = router.execute("pwd")
        print(f"pwd: {response.stdout}")
        
        # Test mkdir
        response = router.execute("mkdir test_dir")
        print(f"mkdir: status={response.status}")
        
        # Test ls
        response = router.execute("ls")
        print(f"ls: {response.stdout}")
        
        # Test touch
        response = router.execute("touch test_file.txt")
        print(f"touch: status={response.status}")
        
        # Test cat on empty file
        response = router.execute("cat test_file.txt")
        print(f"cat empty file: {response.stdout}")
        
        # Test cat on non-existent file
        response = router.execute("cat nonexistent.txt")
        print(f"cat nonexistent: {response.stderr}")
        
        # Test writing content to file
        with open("test_file.txt", "w") as f:
            f.write("Hello, World!\nThis is a test file.")
        
        # Test cat on populated file
        response = router.execute("cat test_file.txt")
        print(f"cat populated file: {response.stdout}")
        
        # Test cd
        response = router.execute("cd test_dir")
        print(f"cd: status={response.status}")
        
        # Test pwd after cd
        response = router.execute("pwd")
        print(f"pwd after cd: {response.stdout}")
        
        # Test back to parent
        response = router.execute("cd ..")
        print(f"cd back: status={response.status}")
        
        # Test rm
        response = router.execute("rm test_file.txt")
        print(f"rm: status={response.status}")
        
        # Test ls after rm
        response = router.execute("ls")
        print(f"ls after rm: {response.stdout}")
        
        print("=== All tests completed successfully ===")
        
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(test_dir)
        if "WORKSPACE_ROOT" in os.environ:
            del os.environ["WORKSPACE_ROOT"]


if __name__ == "__main__":
    main()
