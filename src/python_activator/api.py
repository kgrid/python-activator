from fastapi import FastAPI, Request, Header
import sys
import uvicorn
import importlib
from importlib import util, metadata
import os
from os import path
import subprocess
import yaml
import json
from pathlib import Path

app = FastAPI()
KnowledgeObjects = (
    {}
)  # this dictionary used to keep loaded objects (key:is and value:function)
object_directory = ""  # used for location of knowledge objects


@app.get("/")
def hello():
    return {"Hello": "World9"}


@app.post("/endpoints")
def hello():
    return {"Hello": "test"}


# end point to expose all packages
@app.post("/ep/{endpoint_key:path}")
async def execute_endpoint(
    endpoint_key: str, request: Request, content_type: str = Header(...)
):
    # get the method
    function = KnowledgeObjects[endpoint_key]
    if function:
        # run the imported method and pass the request json
        # if content_type == 'application/json':
        data = await request.json()
        # else:
        #   data="test"

        result = function(data)

        return {"result": result}
    else:
        return {"result": "Knowledge object not found!"}


# Install requirements using the requirements.txt file for each package
def install_requirements(modulepath):
    dependency_requirements = modulepath + "requirements.txt"

    # uses 'pip install -r requirements.txt' to install requirements
    if path.exists(dependency_requirements):
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", dependency_requirements]
        )


# look into the main directory that has all the packages and have the python ones installed
def install_packages_from_directory(directory):
    ko_folders = [f.name for f in os.scandir(directory) if f.is_dir()]
    sys.path.append(
        directory
    )  # temporarily add external packages directory to sys.path to be explorable by python
    for ko_folder in ko_folders:
        install_module(directory, ko_folder)
    sys.path.remove(directory)  # remove external packages directory from sys.path
    list_installed_packages()


def install_module(
    directory, ko_folder
):  # TO DO: test how it works for windows installation
    modulepath = directory + ko_folder + "/"
    install_requirements(modulepath)

    # get metadata and deployment files
    with open(modulepath + "deployment.yaml", "r") as file:
        deployment_data = yaml.safe_load(file)
    with open(modulepath + "metadata.json", "r") as file:
        metadata = json.load(file)

    # import module, get the function and add it to the dictionary
    module_name = (
        ko_folder
        + "."
        + deployment_data["/welcome"]["post"]["entry"].split(".")[0].replace("/", ".")
    )  ##i.e. 'python-multiartifact-v1.0.src.main'
    spec = util.spec_from_file_location(
        module_name, modulepath + deployment_data["/welcome"]["post"]["entry"]
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    mymethod = getattr(module, deployment_data["/welcome"]["post"]["function"])
    KnowledgeObjects[metadata["@id"]] = mymethod


def list_installed_packages():
    print("-------------------\nPackages installed:")
    keys_list = list(KnowledgeObjects.keys())
    print(keys_list)
    print("-------------------")


# run install if the app is starated using poetry run uvicorn python_activator.api:app --reload
# @app.on_event("startup")
# async def startup_event():
#    if sys.argv[0].split("/")[-1]=="uvicorn":
#        print("++++++++++++++++++++++++")
#        run("/home/faridsei/dev/test/pyshelf/")


# run virtual server when running this .py file directly for debugging. It will look for objects at {code folder}/pyshelf
if __name__ == "__main__":
    print(">>>>>running with debug<<<<<")
    install_packages_from_directory("/home/faridsei/dev/test/pyshelf/")
    uvicorn.run(app, host="127.0.0.1", port=8000)

# run install packages from the given OBJECT_PATH if the app is starated using "OBJECT_PATH={your collection path} poetry run uvicorn python_activator.api:app --reload". If running in a virtual environment you could also use "OBJECT_PATH={your collection path} uvicorn python_activator.api:app --reload"
if __name__=="python_activator.api" and sys.argv[0].split("/")[-1]=="uvicorn": 
    if os.environ.get(
        "OBJECT_PATH"
    ):  
        print(">>>>>running with uvicorn<<<<<")
        object_directory = os.environ.get("OBJECT_PATH")
        del os.environ["OBJECT_PATH"]
        install_packages_from_directory(object_directory)
    else:
        print("Attention! No collection path provided.")
        print("Run with the follwoing format:\nOBJECT_PATH={your collection path} poetry run uvicorn python_activator.api:app --reload")
        sys.exit(0)
