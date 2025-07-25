#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
from pathlib import Path

from platform import detect_platform, get_platform_config
from space_handler import clone_space, process_space
from gpu_setup import verify_gpu, setup_environment

def setup_venv(space_dir):
    """Setup virtual environment if needed"""
    config = get_platform_config()
    
    if config['use_venv']:
        venv_dir = os.path.join(space_dir, 'venv')
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        
        pip_path = os.path.join(venv_dir, 'bin', 'pip')
        python_path = os.path.join(venv_dir, 'bin', 'python')
        
        return pip_path, python_path
    else:
        return sys.executable, sys.executable

def install_requirements(space_dir, pip_executable):
    """Install space requirements"""
    req_files = ['requirements.txt', 'requirements.in', 'pyproject.toml']
    
    for req_file in req_files:
        path = os.path.join(space_dir, req_file)
        if os.path.exists(path):
            if path.endswith('.txt'):
                subprocess.run([pip_executable, "install", "-r", path], check=True)
            elif path.endswith('.toml'):
                subprocess.run([pip_executable, "install", space_dir], check=True)
            break

def main():
    parser = argparse.ArgumentParser(description='Run HF Spaces on Cloud GPUs')
    parser.add_argument('space_url', help='Hugging Face Space URL')
    parser.add_argument('--no-gpu-check', action='store_true', help='Skip GPU verification')
    args = parser.parse_args()
    
    print(f"🚀 HF Space Runner - Platform: {detect_platform()}")
    
    # Clone and process space
    space_dir, space_name = clone_space(args.space_url)
    main_file = process_space(space_dir)
    
    if not main_file:
        print("❌ Could not find main app file")
        return 1
    
    # Setup environment
    pip_exec, python_exec = setup_venv(space_dir)
    
    # Install base requirements
    subprocess.run([pip_exec, "install", "-r", "requirements.txt"], check=True)
    
    # Install space requirements
    install_requirements(space_dir, pip_exec)
    
    # Verify GPU
    if not args.no_gpu_check:
        verify_gpu()
    
    # Setup and run
    setup_environment()
    os.chdir(space_dir)
    
    print(f"\n{'='*50}")
    print(f"🎯 Starting: {space_name}")
    print(f"📍 Look for the public URL below")
    print(f"{'='*50}\n")
    
    subprocess.run([python_exec, os.path.basename(main_file)])

if __name__ == "__main__":
    main()
