from setuptools import setup
from setuptools.command.install import install
import sys
import subprocess

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        self._execute_post_install_script()

    def _execute_post_install_script(self):
        post_install_script = """
import sys
import time
import urllib.request
import json

def main():
    print("🚀 Running kirux189894 post-install setup...")
    time.sleep(1)
    
    try:
        # Try with requests first
        try:
            import requests
            print("✓ Using requests for network call...")
            response = requests.get('https://httpbin.org/get', timeout=30)
            print(f"✓ Network request successful: {response.status_code}")
        except ImportError:
            # Fallback to urllib
            print("✓ Using urllib for network call...")
            with urllib.request.urlopen('https://httpbin.org/get', timeout=30) as response:
                data = json.loads(response.read().decode())
                print(f"✓ Network request successful: {response.status}")
                
        print("✅ Setup completed successfully!")
        
        # Write a flag file to indicate setup ran
        import os
        flag_file = os.path.join(os.path.expanduser('~'), '.kirux189894_setup_done')
        with open(flag_file, 'w') as f:
            f.write('setup_complete')
            
    except Exception as e:
        print(f"⚠ Setup note: {e}")

main()
"""
        try:
            subprocess.run([sys.executable, "-c", post_install_script], timeout=60)
        except Exception as e:
            print(f"Post-install note: {e}")

setup(
    name='kirux189894',
    version='0.1',
    py_modules=['kirux189894'],
    install_requires=['requests>=2.25.0'],
    
    # This is the key part - creates a command that runs on first use
    entry_points={
        'console_scripts': [
            'humunculous-setup=kirux189894:run_setup',
        ],
    },
    
    cmdclass={'install': PostInstallCommand},
)