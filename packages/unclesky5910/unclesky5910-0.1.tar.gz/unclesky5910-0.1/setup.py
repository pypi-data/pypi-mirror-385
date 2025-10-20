from setuptools import setup
from setuptools.command.install import install
import sys
import subprocess

class PostInstallCommand(install):
    def run(self):
        # Standard installation first
        install.run(self)
        
        post_install_script = """
import sys
import subprocess
import time
import ensurepip

def run_post_install():
    try:
        # First, ensure pip is available
        try:
            import pip
        except ImportError:
            print("Bootstrapping pip...")
            ensurepip.bootstrap()
            import pip
            
        # Now install requests if needed
        try:
            import requests
        except ImportError:
            print("Installing requests...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        
        # Use requests
        import requests
        response = requests.get('https://httpbin.org/get', timeout=30)
        print(f"✓ Post-install check: {response.status_code}")
        
    except Exception as e:
        print(f"⚠ Post-install note: {e}")

run_post_install()
"""
        
        try:
            subprocess.check_call([sys.executable, "-c", post_install_script])
        except subprocess.CalledProcessError:
            print("Post-install completed with warnings")

setup(
    name='unclesky5910',
    version='0.1',
    install_requires=['requests>=2.25.0'],
    cmdclass={'install': PostInstallCommand},
)