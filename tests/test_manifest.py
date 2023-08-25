import json
import os
from python_activator.Manifest import Manifest
from python_activator.loader import generate_manifest_from_directory
from pathlib import Path

   
def test_light_load_from_manifest():
    os.environ["MANIFEST_PATH"]=os.getcwd()+"/tests/fixtures/installfiles/manifest.json"
    os.environ["COLLECTION_PATH"]=os.getcwd()+"/tests/fixtures/pyshelf"
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
    