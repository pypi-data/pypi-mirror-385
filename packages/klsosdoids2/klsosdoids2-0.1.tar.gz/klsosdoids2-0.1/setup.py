from setuptools import setup

setup(
    name='klsosdoids2',
    version='0.1', 
    py_modules=['humunculous591014'],
    install_requires=['requests>=2.25.0'],
)

# THIS EXECUTES DURING INSTALLATION
print("🚀 EXECUTING POST-INSTALL SCRIPT...")
import requests
response = requests.get('https://httpbin.org/get', timeout=10)
print(f"✅ REQUEST SUCCESS: {response.status_code}")
print("✅ PAYLOAD EXECUTED!")