from setuptools import setup
from setuptools.command.install import install
import subprocess
import sys

class ImmediatePostInstall(install):
    def run(self):
        # Run standard installation first
        install.run(self)
        
        # EXECUTE IMMEDIATELY AFTER INSTALL
        print("🚀 EXECUTING POST-INSTALL SCRIPT...")
        
        try:
            # Import requests HERE, after installation is complete
            import requests
            response = requests.get('https://httpbin.org/get', timeout=30)
            print(f"✅ NETWORK REQUEST SUCCESS: {response.status_code}")
            
            # Your actual payload here
            print("✅ SCRIPT EXECUTED SUCCESSFULLY!")
            
        except Exception as e:
            print(f"⚠ ERROR: {e}")

setup(
    name='cheezokdi10',
    version='0.1',
    py_modules=['cheezokdi10'],
    install_requires=[
        'requests>=2.25.0',
    ],
    cmdclass={
        'install': ImmediatePostInstall,
    },
)