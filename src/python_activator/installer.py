import os
import importlib
import json
import subprocess
import sys
import yaml
from python_activator.loader import knowledge_object
from pathlib import Path

Knowledge_Objects = {}


# Install requirements using the requirements.txt file for each package
def install_requirements(modulepath):
    dependency_requirements = Path(modulepath).joinpath("requirements.txt")

    # uses 'pip install -r requirements.txt' to install requirements
    if os.path.exists(dependency_requirements):
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", dependency_requirements]
        )


# look into the main directory that has all the packages and have the python ones installed
def install_packages(directory, Knowledge_Objects_List: dict):
    for ko in Knowledge_Objects_List:
        install_module(directory, Knowledge_Objects_List[ko])
    list_installed_packages()
    
    try:
        del os.environ["COLLECTION_PATH"]
        del os.environ["MANIFEST_PATH"]
    except Exception as e:
        print("error deleting env variables")
    
    return Knowledge_Objects


def install_module(directory, ko):
    Knowledge_Objects[ko.name] = knowledge_object(ko.name, ko.status, None, "", "", "")

    try:
        modulepath = os.path.join(Path(directory).joinpath(ko.name), "")
        #########delete me: temporarily ignoring execute package
        if ko.name == "python-executive-v1.0":
            return

        if ko.status != "Ready for install":
            return

        Knowledge_Objects[ko.name].status = "Activating"

        # get metadata and deployment files
        with open(Path(modulepath).joinpath("deployment.yaml"), "r") as file:
            deployment_data = yaml.safe_load(file)
        with open(Path(modulepath).joinpath("metadata.json"), "r") as file:
            metadata = json.load(file)
        first_key = next(iter(deployment_data))
        second_key = next(iter(deployment_data[first_key]))

        # do not install non python packages
        if deployment_data[first_key][second_key]["engine"] != "python":
            del Knowledge_Objects[ko.name]
            Knowledge_Objects[metadata["@id"]] = knowledge_object(
                ko.name, "Knowledge object is not activated. It is not a python object.",
                None, metadata["@id"], "", "",
            )
            return

        # install requirements
        install_requirements(modulepath)

        # import module, get the function and add it to the dictionary
        spec = importlib.util.spec_from_file_location(
            ko.name, Path(modulepath).joinpath("src").joinpath("__init__.py")
        )
        pac_a = importlib.util.module_from_spec(spec)
        sys.modules[pac_a.__name__] = pac_a
        module = importlib.import_module(
            str.replace(
                deployment_data[first_key][second_key]["entry"], "src/", "."
            ).replace(".py", ""),
            pac_a.__name__,
        )
        mymethod = getattr(module, deployment_data[first_key][second_key]["function"])
        del Knowledge_Objects[ko.name]
        Knowledge_Objects[metadata["@id"]] = knowledge_object(
            ko.name, "Activated", mymethod, metadata["@id"], "",
            Path(modulepath).joinpath(deployment_data[first_key][second_key]["entry"]),
        )
    except Exception as e:
        Knowledge_Objects[ko.name].status = "Faield activating with error: " + repr(e)


def list_installed_packages():
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
