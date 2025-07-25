import os

def detect_platform():
    """Detect which cloud platform we're running on"""
    if 'LIGHTNING_CLOUD_APP_ID' in os.environ:
        return 'lightning'
    elif 'COLAB_GPU' in os.environ:
        return 'colab'
    elif os.path.exists('/opt/conda'):
        return 'vast'
    else:
        return 'unknown'

def get_platform_config():
    """Get platform-specific configuration"""
    platform = detect_platform()
    
    config = {
        'platform': platform,
        'use_venv': platform in ['vast', 'colab'],
        'gpu_available': True,  # Assume GPU platform
    }
    
    return config
