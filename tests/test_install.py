import subprocess
import importlib
import os
from python_activator.Manifest import Manifest

def test_installing_knowledgeobject_programatically():
    #load
    os.environ["ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH"]=os.getcwd()+"/tests/fixtures/installfiles/manifest.json"
    os.environ["ORG_KGRID_PYTHON_ACTIVATOR_COLLECTION_PATH"]=os.getcwd()+"/tests/fixtures/pyshelf"
    manifest=Manifest()
    ko_list=manifest.load_from_manifest()
    
    #install
    package_path = "tests/fixtures/pyshelf/python-simple-v1-0/"
    try:
    # Using subprocess.run for Python 3.5+
        subprocess.run(["pip", "install", package_path], check=True)
        print("success.")
        module_spec = importlib.util.find_spec("python_simple_v1_0")
        
    except subprocess.CalledProcessError:
        print("Failed to install the package.")
        
    assert module_spec is not None, f"Package not found."    
        
