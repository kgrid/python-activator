import importlib
import sys
sys.path.append("/home/faridsei/dev/test/pyshelf")
spec = importlib.util.spec_from_file_location("python-multiartifact_v1_0.src.main", "/home/faridsei/dev/test/pyshelf/python-multiartifact_v1_0/src/main.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sys.path.remove("/home/faridsei/dev/test/pyshelf")
mymethod = getattr(
                module, "generate_page"
            )
