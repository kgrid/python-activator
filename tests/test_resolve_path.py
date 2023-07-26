from http.client import InvalidURL
import pytest
from python_activator.loader import resolve_path    

    ######url manifest
def test_url_manifest_and_relative_item1():   
    resolved=resolve_path("https://github.com/kgrid/collections/manifest.json",
        "smple-python.zip")
    expected="https://github.com/kgrid/collections/smple-python.zip"
    assert resolved==expected
    
def test_url_manifest_and_relative_item2():   
    resolved=resolve_path("https://github.com/kgrid/collections/manifest.json",
        "zipfiles/smple-python.zip")
    expected="https://github.com/kgrid/collections/zipfiles/smple-python.zip"
    assert resolved==expected    
    
def test_url_manifest_and_url_item():   
    resolved=resolve_path("https://github.com/kgrid/collections/manifest.json",
        "https://github.com/kgrid/collections/smple-python.zip")
    expected="https://github.com/kgrid/collections/smple-python.zip"
    assert resolved==expected        
    
def test_url_manifest_and_absolute_item():  #incorrect manifest  
    resolved=resolve_path("https://github.com/kgrid/collections/manifest.json",
        "/home/tests/zipfiles/smple-python.zip")
    expected="https://github.com/home/tests/zipfiles/smple-python.zip"
    assert resolved==expected     
    
def test_url_manifest_and_nothing():  #incorrect manifest  
    resolved=resolve_path("https://github.com/kgrid/collections/manifest.json",
        "")
    expected="https://github.com/kgrid/collections/manifest.json"
    assert resolved==expected       
    




    ########Path manifest    
def test_absolute_manifest_and_relative_item1():   
    resolved=resolve_path("file:///example/resources/manifest.json",
        "smple-python.zip")
    expected="file:///example/resources/smple-python.zip"
    assert resolved==expected
    
def test_absolute_manifest_and_relative_item2():   
    resolved=resolve_path("file:///example/resources/manifest.json",
        "zipfiles/smple-python.zip")
    expected="file:///example/resources/zipfiles/smple-python.zip"
    assert resolved==expected    
    
def test_absolute_manifest_and_url_item():   
    resolved=resolve_path("file:///example/resources/manifest.json",
        "https://github.com/kgrid/collections/smple-python.zip")
    expected="https://github.com/kgrid/collections/smple-python.zip"
    assert resolved==expected        
    
def test_absolute_manifest_and_absolute_item():  #incorrect manifest  
    resolved=resolve_path("file:///example/resources/manifest.json",
        "/home/tests/zipfiles/smple-python.zip")
    expected="file:///home/tests/zipfiles/smple-python.zip"
    assert resolved==expected     
    
def test_absolute_manifest_and_nothing():  #incorrect manifest  
    resolved=resolve_path("file:///example/resources/manifest.json",
        "")
    expected="file:///example/resources/manifest.json"
    assert resolved==expected      
    
  
