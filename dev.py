#!/usr/bin/env python
import os
import sys
import subprocess
import threading
import time
import signal

def run_flask_backend():
    """Run the Flask backend server using UV."""
    backend_env = os.environ.copy()
    backend_env['PORT'] = '8080'
    print("Ensuring dependencies are installed...")
    
    # Install dependencies using uv sync if needed
    try:
        subprocess.run(['uv', 'sync'], check=True)
    except subprocess.CalledProcessError:
        print("⚠️ Failed to sync dependencies. Make sure your virtual environment is activated.")
    
    # Run the Flask app with uv
    backend_process = subprocess.Popen(
        ['uv', 'run', 'flask', '--app', 'backend.app', 'run', '--host=0.0.0.0', '--port=8080'],
        env=backend_env
    )
    return backend_process

def run_nextjs_frontend():
    """Run the Next.js frontend development server."""
    frontend_env = os.environ.copy()
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    
    # Add environment variables for the frontend
    frontend_env.update({
        'NEXT_PUBLIC_API_URL': 'http://localhost:8080',
        'NODE_ENV': 'development'
    })
    
    # Don't change directory for the whole process, use cwd parameter instead
    frontend_process = subprocess.Popen(
        ['npm', 'run', 'dev'],
        env=frontend_env,
        cwd=frontend_dir
    )
    return frontend_process

def check_frontend_dependencies():
    """Check if frontend dependencies are installed, install if needed."""
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    node_modules_path = os.path.join(frontend_dir, 'node_modules')
    
    if not os.path.exists(node_modules_path):
        print("📦 Frontend dependencies not found. Installing...")
        subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
        print("✅ Frontend dependencies installed successfully.")
    
def check_virtual_environment():
    """Check if we're running in a virtual environment."""
    if not hasattr(sys, 'base_prefix') or sys.base_prefix == sys.prefix:
        print("⚠️ Virtual environment not detected. It's recommended to run this script within a virtual environment.")
        print("   You can create and activate one with:")
        print("     python -m venv .venv")
        print("     source .venv/bin/activate  # On macOS/Linux")
        print("     .venv\\Scripts\\activate     # On Windows")
        
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting. Please activate your virtual environment and try again.")
            sys.exit(1)
    else:
        print("✅ Virtual environment detected.")

def main():
    """Run both backend and frontend servers."""
    print("Starting development servers...")
    
    try:
        # Check if running in a virtual environment
        check_virtual_environment()
        
        # Check and install frontend dependencies if needed
        check_frontend_dependencies()
        
        # Start backend
        print("Starting Flask backend on http://localhost:8080...")
        backend_process = run_flask_backend()
        
        # Wait a moment for backend to initialize
        time.sleep(2)
        
        # Start frontend
        print("Starting Next.js frontend on http://localhost:3000...")
        frontend_process = run_nextjs_frontend()
        
        print("\n✅ Development environment is running!")
        print("- Backend API: http://localhost:8080")
        print("- Frontend: http://localhost:3000")
        print("\nPress Ctrl+C to stop both servers\n")
        
        # Wait for both processes
        try:
            while True:
                # Check if processes are still running
                if backend_process.poll() is not None:
                    print("⚠️ Backend process exited unexpectedly with code:", backend_process.returncode)
                    break
                
                if frontend_process.poll() is not None:
                    print("⚠️ Frontend process exited unexpectedly with code:", frontend_process.returncode)
                    break
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down servers...")
    except Exception as e:
        print(f"Error starting development servers: {str(e)}")
    finally:
        # Clean up processes in finally block to ensure they are terminated
        try:
            if 'backend_process' in locals():
                backend_process.terminate()
                backend_process.wait(timeout=5)
        except:
            print("Could not cleanly terminate backend process")
        
        try:
            if 'frontend_process' in locals():
                frontend_process.terminate()
                frontend_process.wait(timeout=5)
        except:
            print("Could not cleanly terminate frontend process")
        
        print("Servers have been shut down.")

if __name__ == "__main__":
    main()