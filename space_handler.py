import os
import re
import shutil
from pathlib import Path
from huggingface_hub import snapshot_download

def clone_space(space_url):
    """Clone a Hugging Face Space from URL"""
    pattern = r'https://huggingface\.co/spaces/([^/]+)/([^/]+)'
    match = re.match(pattern, space_url.strip())
    
    if not match:
        raise ValueError("Invalid Hugging Face Space URL format")
    
    username, space_name = match.groups()
    repo_id = f"{username}/{space_name}"
    local_dir = f"./hf_space_{space_name}"
    
    if os.path.exists(local_dir):
        shutil.rmtree(local_dir)
    
    print(f"Cloning space: {repo_id}")
    snapshot_download(
        repo_id=repo_id,
        repo_type="space",
        local_dir=local_dir,
        ignore_patterns=["*.git*", "*.md", "README.md"]
    )
    
    return local_dir, space_name

def remove_zero_gpu(file_path):
    """Remove @spaces.GPU decorator and imports"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    patterns = [
        r'from\s+spaces\s+import\s+GPU',
        r'import\s+spaces',
        r'from\s+spaces\s+import\s+\*',
        r'@spaces\.GPU[^\n]*\n',
        r'@GPU[^\n]*\n',
    ]
    
    modified = content
    for pattern in patterns:
        modified = re.sub(pattern, '', modified)
    
    modified = re.sub(r'@spaces\.GPU[^\n]*(\s*def\s+)', r'\1', modified)
    modified = re.sub(r'@GPU[^\n]*(\s*def\s+)', r'\1', modified)
    
    if modified != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified)
        return True
    return False

def modify_gradio_launch(file_path):
    """Enable Gradio sharing and cloud-friendly settings"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    def replace_launch(match):
        launch_call = match.group(0)
        if 'share=' in launch_call:
            new_call = re.sub(r'share\s*=\s*\w+', 'share=True', launch_call)
        else:
            if launch_call.strip().endswith('()'):
                new_call = launch_call[:-2] + 'share=True)'
            else:
                new_call = launch_call[:-1] + ', share=True)'
        
        if 'server_name=' not in new_call:
            new_call = new_call[:-1] + ', server_name="0.0.0.0")'
        
        return new_call
    
    modified = re.sub(r'\.launch\s*\([^)]*\)', replace_launch, content)
    
    if modified != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified)
        return True
    return False

def process_space(space_dir):
    """Process all Python files in the space"""
    python_files = list(Path(space_dir).glob('**/*.py'))
    
    # Remove Zero GPU references
    for py_file in python_files:
        remove_zero_gpu(py_file)
    
    # Find and modify main app file
    app_files = ['app.py', 'main.py', 'demo.py', 'gradio_app.py']
    main_file = None
    
    for app_file in app_files:
        path = os.path.join(space_dir, app_file)
        if os.path.exists(path):
            main_file = path
            modify_gradio_launch(path)
            break
    
    if not main_file:
        for py_file in python_files:
            with open(py_file, 'r', encoding='utf-8') as f:
                if '.launch(' in f.read():
                    main_file = py_file
                    modify_gradio_launch(py_file)
                    break
    
    return main_file
