#!/usr/bin/env python3
"""
Example usage of the command router and registry.
"""

from core.router import CommandRouter
from core.registry import CommandRegistry
from core.session import SessionContext


def echo_handler(*args):
    """Simple echo command handler."""
    return {"stdout": " ".join(args), "status": 0}


def pwd_handler():
    """Print working directory command handler."""
    return {"stdout": "/current/directory", "status": 0}


def main():
    # Create registry and session
    registry = CommandRegistry()
    session = SessionContext()
    
    # Register some commands
    registry.register("echo", echo_handler, "Echo arguments", ["message"])
    registry.register("pwd", pwd_handler, "Print working directory", [])
    
    # Create router
    router = CommandRouter(registry, session)
    
    # Test some commands
    print("Testing router...")
    
    # Test help
    response = router.execute("help")
    print("Help response:")
    print(f"stdout: {response.stdout}")
    print(f"stderr: {response.stderr}")
    print(f"status: {response.status}")
    print()
    
    # Test pwd command (no args required)
    response = router.execute("pwd")
    print("Pwd response:")
    print(f"stdout: {response.stdout}")
    print(f"stderr: {response.stderr}")
    print(f"status: {response.status}")
    print(f"exec_ms: {response.meta['exec_ms'] if response.meta else 'N/A'}")
    print()
    
    # Test echo with proper arguments
    response = router.execute("echo Hello World")
    print("Echo response:")
    print(f"stdout: {response.stdout}")
    print(f"stderr: {response.stderr}")
    print(f"status: {response.status}")
    print(f"exec_ms: {response.meta['exec_ms'] if response.meta else 'N/A'}")
    print()
    
    # Test unknown command
    response = router.execute("unknown")
    print("Unknown command response:")
    print(f"stdout: {response.stdout}")
    print(f"stderr: {response.stderr}")
    print(f"status: {response.status}")
    print()
    
    # Test empty input
    response = router.execute("")
    print("Empty input response:")
    print(f"stdout: {response.stdout}")
    print(f"stderr: {response.stderr}")
    print(f"status: {response.status}")


if __name__ == "__main__":
    main()
