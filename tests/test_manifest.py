import json
import os, shutil
from python_activator.Manifest import Manifest
from python_activator.loader import generate_manifest_from_directory
from pathlib import Path
import pytest

def test_from_manifest_without_manifest():
    if os.path.isdir("/tests/fixtures/pyshelf"):
        shutil.rmtree(os.getcwd()+"/tests/fixtures/pyshelf")
    os.environ["ORG_KGRID_PYTHON_ACTIVATOR_COLLECTION_PATH"]=os.getcwd()+"/tests/fixtures/pyshelf"
    manifest=Manifest()
    try:
        ko_list=manifest.load_from_manifest()
    except Exception as e:
        pytest.fail(f"Function load_from_manifest() raised an exception: {e}")
   
def test_light_load_from_manifest():
    if os.path.isdir("/tests/fixtures/pyshelf"):
        shutil.rmtree(os.getcwd()+"/tests/fixtures/pyshelf")
    
    os.environ["ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH"]=os.getcwd()+"/tests/fixtures/installfiles/manifest.json"
    os.environ["ORG_KGRID_PYTHON_ACTIVATOR_COLLECTION_PATH"]=os.getcwd()+"/tests/fixtures/pyshelf"
    manifest=Manifest()
    ko_list=manifest.load_from_manifest()
    assert ko_list[0].status=="loaded"
    
def test_generate_manifest_from_directory():
    try:
        os.remove("tests/fixtures/pyshelf/local_manifest.json")
    except:
        pass
    generate_manifest_from_directory("tests/fixtures/pyshelf")
    assert Path("tests/fixtures/pyshelf/local_manifest.json").exists()
    with open("tests/fixtures/pyshelf/local_manifest.json", 'r') as json_file:
        data = json.load(json_file)
    assert data[0]["@id"]
    assert data[0]["local_url"]
    