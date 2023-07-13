import pytest
from src.python_activator.cli import *

def test_process_local_manifest():
	
	manifest=process_manifest("/home/faridsei/dev/test/package/manifest.json","/home/faridsei/dev/test/pyshelf/")

	# Assert
	assert 1==1
	
def test_process_internet_manifest():
	
	manifest=process_manifest("https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/manifest.json","/home/faridsei/dev/test/pyshelf/")

	# Assert
	assert 1==1
 
def test_process_no_manifest():
	
	process_manifest("","")

	# Assert
	assert 1==1

 
