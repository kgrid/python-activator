from typing import Union
from fastapi import FastAPI, Request, Header
import sys
import uvicorn
import importlib
import os
from os import path
import subprocess
import yaml
import json 
app = FastAPI()

KnowledgeObjects = {}


@app.get("/")
def hello():
    return {"Hello": "World9"}


@app.post("/test/test1")
def hello():
    return {"Hello": "test"}

#end point to expose all packages
@app.post("/{endpoint_key:path}")
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
        return {"result": "ko not found!"}


#Install requirements using the requirements.txt file for each package
def install_requirements(modulepath):
    dependency_requirements = modulepath + "requirements.txt"

    # uses 'pip install -r requirements.txt' to install requirements
    if path.exists(dependency_requirements):
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", dependency_requirements]
        )


#crowl the main dorectory that has all the packages and have them installed
def object_crawler(directory):
    ko_folders = [f.name for f in os.scandir(directory) if f.is_dir()]
    for ko_folder in ko_folders:
        install_module(directory , ko_folder)


def install_module(directory, ko_folder):
    modulepath=directory + ko_folder + "/"
    install_requirements(
        modulepath,
    )

    # TO DO: test how it works for windows installation

    # get metadata and deployment files
    with open(modulepath + "deployment.yaml", "r") as file:
        prime_service = yaml.safe_load(file)
        
    with open(modulepath + "metadata.json", 'r') as file:
        data = json.load(file)    
        

    sys.path.append(directory)
    module_name=ko_folder+"."+prime_service["/welcome"]["post"]["entry"].split(".")[
        0
    ].replace("/",".")  ##i.e. 'python-multiartifact-v1.0.src.main'
    spec = importlib.util.spec_from_file_location(module_name, modulepath+prime_service["/welcome"]["post"]["entry"])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.path.remove(directory)
    
    mymethod = getattr(
                    module, prime_service["/welcome"]["post"]["function"]
                )
    KnowledgeObjects[data["@id"]] = mymethod


object_crawler("/home/faridsei/dev/test/pyshelf/") #temporarily hardcode the path that contains knowledge objects here


# only runs virtual server when running this .py file directly for debugging
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
