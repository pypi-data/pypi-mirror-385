"""
kirux189894 package
"""

import sys
import os
import urllib.request
import json

__version__ = '0.1'
__author__ = 'Your Name'

def run_setup():
    """This runs when user types 'humunculous-setup' in terminal"""
    print("🚀 Running kirux189894 setup...")
    
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
        return True
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def hello():
    """Example function"""
    return "Hello from kirux189894!"

# Auto-run setup when module is imported (optional)
def _auto_setup():
    flag_file = os.path.join(os.path.expanduser('~'), '.kirux189894_auto_setup')
    if not os.path.exists(flag_file):
        print("🔧 Running auto-setup for kirux189894...")
        if run_setup():
            # Create flag file so it doesn't run again
            with open(flag_file, 'w') as f:
                f.write('auto_setup_complete')
        else:
            print("⚠ Auto-setup failed, will try again next time")

# Uncomment the line below if you want setup to run on first import
# _auto_setup()