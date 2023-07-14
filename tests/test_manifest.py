import pytest
from src.python_activator.api import *

def test_process_local_manifest():
	os.environ["MANIFEST_PATH"]="/home/faridsei/dev/test/package/manifest.json"
	process_manifest("/home/faridsei/dev/test/pyshelf/")
	del os.environ["MANIFEST_PATH"]


	# Assert
	assert 1==1
	
def test_process_internet_manifest():
	os.environ["MANIFEST_PATH"]="https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/manifest.json"
	process_manifest("/home/faridsei/dev/test/pyshelf/")
	del os.environ["MANIFEST_PATH"]

	# Assert
	assert 1==1
 
def test_process_no_manifest():
	
	process_manifest("/home/faridsei/dev/test/pyshelf/")

	# Assert
	assert 1==1

 
def test_using_uri_to_download_zip():
    assert 1!=1
    
def test_formatting_dictionary_of_object_to_json():
    assert 1!=1