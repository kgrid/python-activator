import subprocess
import importlib

def test_installing_knowledgeobject_programatically():
    package_path = "tests/fixtures/pyshelf/python-simple-v1-0/"
    try:
    # Using subprocess.run for Python 3.5+
        subprocess.run(["pip", "install", package_path], check=True)
        print("success.")
        module_spec = importlib.util.find_spec("python_simple_v1_0")
        
    except subprocess.CalledProcessError:
        print("Failed to install the package.")
        
    assert module_spec is not None, f"Package not found."    
        
