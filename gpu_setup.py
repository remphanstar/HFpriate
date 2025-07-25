import subprocess
import sys

def verify_gpu():
    """Verify GPU availability"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ GPU Available: {torch.cuda.get_device_name(0)}")
            print(f"✓ CUDA Version: {torch.version.cuda}")
            return True
        else:
            print("⚠ No GPU detected. Running on CPU.")
            return False
    except ImportError:
        print("PyTorch not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "torch"], check=True)
        return verify_gpu()

def setup_environment():
    """Set GPU environment variables"""
    import os
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    os.environ['GRADIO_SERVER_NAME'] = '0.0.0.0'
    os.environ['GRADIO_SERVER_PORT'] = '7860'
