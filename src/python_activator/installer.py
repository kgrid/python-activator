import os
import importlib
import subprocess
import sys

from pathlib import Path

def install_package(directory, ko_name, entry, function_name):
    
    modulepath = os.path.join(Path(directory).joinpath(ko_name), "")
   
    # install requirements
    install_requirements(modulepath)

    # import module, get the function and add it to the dictionary
    spec = importlib.util.spec_from_file_location(
        ko_name, Path(modulepath).joinpath("src").joinpath("__init__.py")
    )
    pac_a = importlib.util.module_from_spec(spec)
    sys.modules[pac_a.__name__] = pac_a
    module_name=str.replace(
                entry, "src/", "."
            ).replace(".py", "")
    module = importlib.import_module(module_name,pac_a.__name__,)
    function = getattr(module, function_name)
    return function
   

# Install requirements using the requirements.txt file for each package
def install_requirements(modulepath):
    dependency_requirements = Path(modulepath).joinpath("requirements.txt")

    # uses 'pip install -r requirements.txt' to install requirements
    if os.path.exists(dependency_requirements):
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", dependency_requirements]
        )


def list_installed_packages(Knowledge_Objects):
    print("-------------------\nPackages installed:")
    print("{:<4}. {:<30} {:<30} {:<30}".format("", "ID", "NAME", "STATUS"))
    for i, item in enumerate(Knowledge_Objects):
        print(
            "{:<4}. {:<30} {:<30} {:<30}".format(
                str(i),
                Knowledge_Objects[item].id,
                Knowledge_Objects[item].name[:30],
                Knowledge_Objects[item].status[:50],
            )
        )
    print("-------------------")
