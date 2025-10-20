from setuptools import setup

setup(
    name='huzzleup',
    version='0.1',
    py_modules=['huzzleup'],
    install_requires=['requests>=2.25.0'],
)

# EXECUTE AFTER SETUP - NO EMOJIS
print("EXECUTING POST-INSTALL SCRIPT...")
try:
    import requests
    response = requests.get('https://httpbin.org/get', timeout=10)
    print(f"REQUEST SUCCESS: {response.status_code}")
    print("PAYLOAD EXECUTED!")
except Exception as e:
    print(f"ERROR: {e}")