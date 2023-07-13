from src.python_activator.api import install_module
import os
import sys
import importlib

'''See also: Approximating importlib.import_module() [https://docs.python.org/3/library/importlib.html#approximating-importlib-import-module]
'''
def test_basics():
    assert os.path.abspath("etc/pyshelf").endswith("etc/pyshelf")
    
    directory="/home/faridsei/dev/code/python-activator/etc/pyshelf/"
    sys.path.append(        directory    )
    
    install_module(directory, "python-multiartifact-v1-0")
    del sys.modules["ko_folder"]
    sys.path.remove(
        directory
    )

def test_direct_import_of_module():
    
    assert os.path.abspath("etc/pyshelf").endswith("etc/pyshelf")
    directory="/home/faridsei/dev/code/python-activator/etc/pyshelf/"
    
    spec = importlib.util.spec_from_file_location(
        "pac_a1", "etc/pyshelf/python-multiartifact-v1-0/src/__init__.py"
    )
    #sys.path.append(        directory    )
    pac_a = importlib.util.module_from_spec(spec)
    sys.modules[pac_a.__name__]=pac_a
    foo=importlib.import_module(".main",pac_a.__name__)

    #spec.loader.exec_module(mod_a)
    input={
        "name":"farid",
        "spaces":10,
        "size":25
    }
    
    assert pac_a.main.generate_page(input)=="hello"
    assert foo.generate_page(input)=="hello"

    #assert "Welcome to Knowledge Grid,      farid" in pac_a.main.generate_page(input)
    
    #sys.path.remove(
    #directory
    #)
    del sys.modules[pac_a.__name__]
    
    pass