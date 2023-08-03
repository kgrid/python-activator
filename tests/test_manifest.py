import json
import os
from python_activator.Manifest import Manifest
from python_activator.loader import generate_manifest_from_directory
from pathlib import Path

def test_generate_manifest_from_directory():
    generate_manifest_from_directory("tests/fixtures/collection")
    test=Path("tests/fixtures/collection/local_manifest.json").exists()
    assert Path("tests/fixtures/collection/local_manifest.json").exists()
    with open("tests/fixtures/collection/local_manifest.json", 'r') as json_file:
        data = json.load(json_file)
    assert data[0]["@id"]=="node/simple/v1.0" 
    assert data[0]["local_url"]=="node-simple-v1.0"
    
def test_light_load_from_manifest():
    os.environ["MANIFEST_PATH"]=os.getcwd()+"/tests/fixtures/installfiles/manifest.json"
    os.environ["COLLECTION_PATH"]=os.getcwd()+"/tests/fixtures/pyshelf"

    manifest=Manifest()
    ko_list=manifest.load_from_manifest()
    assert ko_list[0].status=="Ready for install"
    