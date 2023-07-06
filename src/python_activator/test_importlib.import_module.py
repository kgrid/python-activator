import sys
import importlib
sys.path.append('/home/faridsei/dev/test/package/python-multiartifact-v1.0/')

module=importlib.import_module("src.main")



mymethod = getattr(
                    module, 'generate_page'
                )
print(mymethod({
    "name":"farid",
    "spaces":10,
    "size":25
}))

