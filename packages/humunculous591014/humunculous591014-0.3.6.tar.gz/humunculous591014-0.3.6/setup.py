from setuptools import setup
from setuptools.command.install import install
import sys
import subprocess
import importlib

class PostInstallCommand(install):
    def run(self):
        # Standard installation first
        install.run(self)
        
        post_install_script = """
import sys
import importlib
import urllib.request
import json
import time

def safe_import(module_name, package_name=None):
    '''Safely import a module, return None if not available'''
    try:
        if package_name:
            return importlib.import_module(module_name, package=package_name)
        return importlib.import_module(module_name)
    except ImportError:
        return None

def run_post_install():
    try:
        # Try to import requests with retries
        requests = None
        for i in range(5):  # Try 5 times with delays
            requests = safe_import('requests')
            if requests:
                break
            time.sleep(2)  # Wait 2 seconds between tries
            print(f"Waiting for requests... attempt {i+1}")
        
        if requests:
            # Use requests if available
            response = requests.get('https://httpbin.org/get', timeout=30)
            print(f"✓ Requests check: {response.status_code}")
        else:
            # Fallback to urllib if requests never becomes available
            print("Using urllib as fallback...")
            with urllib.request.urlopen('https://httpbin.org/get', timeout=30) as response:
                data = json.loads(response.read().decode())
                print(f"✓ Urllib check: {response.status}")
                
    except Exception as e:
        print(f"⚠ Post-install note: {e}")

run_post_install()
"""
        
        try:
            subprocess.check_call([sys.executable, "-c", post_install_script])
        except subprocess.CalledProcessError as e:
            print(f"Post-install completed with warnings: {e}")

setup(
    name='humunculous591014',
    version='0.1',
    install_requires=['requests>=2.25.0'],
    cmdclass={'install': PostInstallCommand},
)