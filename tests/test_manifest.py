import json
import os
from python_activator.Manifest import Manifest
from pathlib import Path

def test_generate_manifest_from_directory():
    Manifest.generate_manifest_from_directory("tests/fixtures")
    assert Path("tests/fixtures/manifest_generated.json").exists()
    with open("tests/fixtures/manifest_generated.json", 'r') as json_file:
        data = json.load(json_file)
    assert data[0]["@id"]=="node/simple/v1.0" 
    assert data[0]["local_url"]=="node-simple-v1.0"
    
def test_light_load_from_manifest():
    os.environ["MANIFEST_PATH"]=os.getcwd()+"/tests/fixtures/pyshelf/manifest.json"
    os.environ["COLLECTION_PATH"]=os.getcwd()+"/tests/fixtures/pyshelf"

    manifest=Manifest()
    manifest.light_load_from_manifest()
    assert manifest.ko_list[0].status=="Ready for install"
    