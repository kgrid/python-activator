from src.python_activator.api import install_module
import os

'''See also: Approximating importlib.import_module() [https://docs.python.org/3/library/importlib.html#approximating-importlib-import-module]
'''
def test_basics():
    assert os.path.abspath("etc/pyshelf").endswith("etc/pyshelf")

    # install_module("/Users/pboisver/dev/code-green/python-activator/etc/pyshelf/", "python-multiartifact-v1.0")
