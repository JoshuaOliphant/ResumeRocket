#!/usr/bin/env python3
"""
Test script for section collapsing functionality

This script runs the section collapsing functionality test in a controlled environment.
It starts the ResumeRocket server, sets up the test environment, and runs the test.
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path

# Add parent directory to path to import from parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def ensure_server_running(host="localhost", port=5000, max_wait=30):
    """Check if the server is running, and start it if not"""
    import socket
    import time
    
    # Check if the server is already running
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((host, port))
            print(f"Server already running on {host}:{port}")
            return None  # No need to start a server, return None
    except (socket.error, socket.timeout):
        print(f"Server not running on {host}:{port}, attempting to start...")
    
    # Start the server
    server_process = subprocess.Popen(
        ["python", "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(Path(__file__).resolve().parent.parent)
    )
    
    # Wait for server to start
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
                print(f"Server started on {host}:{port}")
                return server_process
        except (socket.error, socket.timeout):
            time.sleep(1)
            print("Waiting for server to start...")
    
    print(f"Failed to start server within {max_wait} seconds")
    server_process.terminate()
    return None

def run_tests():
    """Run the JavaScript tests for section collapsing"""
    # Ensure we're in the right directory
    js_tests_dir = Path(__file__).resolve().parent / "js_tests"
    
    # Check if package.json exists
    if not (js_tests_dir / "package.json").exists():
        print("Error: package.json not found in js_tests directory")
        return False
    
    # Install dependencies if needed
    print("Installing test dependencies...")
    subprocess.run(["npm", "install"], cwd=str(js_tests_dir), check=True)
    
    # Install Playwright browsers if needed
    print("Setting up Playwright browsers...")
    subprocess.run(["npm", "run", "setup"], cwd=str(js_tests_dir), check=True)
    
    # Run the test
    print("Running section collapsing test...")
    result = subprocess.run(
        ["node", "test_section_collapsing.js"], 
        cwd=str(js_tests_dir)
    )
    
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Test section collapsing functionality")
    parser.add_argument("--no-server", action="store_true", help="Don't start the server (assume it's already running)")
    args = parser.parse_args()
    
    server_process = None
    try:
        # Start server if needed
        if not args.no_server:
            server_process = ensure_server_running()
            if server_process is None:
                print("Server is already running, will not terminate it when done")
            elif server_process is False:  # Failed to start
                print("Failed to ensure server is running")
                return 1
        
        # Run tests
        success = run_tests()
        
        # Print result
        if success:
            print("\n✅ Section collapsing tests passed!")
            return 0
        else:
            print("\n❌ Section collapsing tests failed")
            return 1
            
    finally:
        # Clean up
        if server_process:
            print("Shutting down test server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()

if __name__ == "__main__":
    sys.exit(main())