from fastapi import FastAPI, Request, Header
import sys
import uvicorn
import importlib
from importlib import util, metadata

from os import path
import subprocess
import yaml
import json
import typer
from python_activator.manifest import *

class knowledge_object:
    def __init__(self, name, status, function ,id):
        self.id= id
        self.name = name
        self.status = status
        self.function = function

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, knowledge_object):
            return {'name': obj.name, 'status': obj.status, 'id': obj.id}
        return super().default(obj)

app = FastAPI()
Knowledge_Objects = (
    {}
)

# this dictionary used to keep loaded objects (key:is and value:function)
object_directory = ""  # used for location of knowledge objects


@app.get("/")
def hello():
    return {"Hello": "World9"}


@app.get("/endpoints")
def hello():
    return json.loads(json.dumps(Knowledge_Objects,cls=CustomEncoder, indent=4))



# end point to expose all packages
@app.post("/ep/{endpoint_key:path}")
async def execute_endpoint(
    endpoint_key: str, request: Request, content_type: str = Header(...)
):
    # get the method
    if endpoint_key in Knowledge_Objects:
        function = Knowledge_Objects[endpoint_key].function
        if function and Knowledge_Objects[endpoint_key].status=="Activated":
            # run the imported method and pass the request json
            # if content_type == 'application/json':
            data = await request.json()
            # else:
            #   data="test"

            result = function(data)

            return {"result": result}
        elif Knowledge_Objects[endpoint_key].status!="Activated":
            return {"result": Knowledge_Objects[endpoint_key].status}
        else:
            return {"result": "Knowledge object not found!"}
    else:
        return {"result": "Knowledge object not found!"}


# Install requirements using the requirements.txt file for each package
def install_requirements(modulepath):
    dependency_requirements = modulepath + "requirements.txt"

    # To Do: using pip install bellow explore installing requirements in a folder specific to the ko
    #       you may need to add that folder to the sys.path

    # uses 'pip install -r requirements.txt' to install requirements
    if path.exists(dependency_requirements):
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", dependency_requirements]
        )


# look into the main directory that has all the packages and have the python ones installed
def install_packages_from_directory(directory, manifest: dict):
    for ko in manifest:        
        install_module(directory, manifest[ko])
    list_installed_packages()


def install_module(
    directory, ko
):  # TO DO: test how it works for windows installation
    Knowledge_Objects[ko.name] = knowledge_object(ko.name,ko.status,None,"")

    try:
        modulepath = directory + ko.name + "/"

        #########delete me: temporarily ignoring execute package
        if ko.name == "python-executive-v1.0":
            return
        
        if ko.status!="Ready for install":
            return


        Knowledge_Objects[ko.name].status = "Activating"
        
        # get metadata and deployment files
        with open(modulepath + "deployment.yaml", "r") as file:
            deployment_data = yaml.safe_load(file)
        with open(modulepath + "metadata.json", "r") as file:
            metadata = json.load(file)
        first_key = next(iter(deployment_data))
        second_key = next(iter(deployment_data[first_key]))
        
        # do not install non python packages
        if deployment_data[first_key][second_key]["engine"] != "python":
            del Knowledge_Objects[ko.name]
            Knowledge_Objects[metadata["@id"]] = knowledge_object(ko.name,"Knowledge object is not activated. It is not a python object.",None,metadata["@id"])
            return

        # install requirements
        install_requirements(modulepath)

        # import module, get the function and add it to the dictionary
        spec = importlib.util.spec_from_file_location(
            ko.name, modulepath + "/src/__init__.py"
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
        Knowledge_Objects[metadata["@id"]] = knowledge_object(ko.name,"Activated",mymethod,metadata["@id"])
    except Exception as e:
        Knowledge_Objects[ko.name].status="Faield activating with error: "+ repr(e)

def list_installed_packages():
    print("-------------------\nPackages installed:")
    #keys_list = list(KnowledgeObjects.keys())
    print("{:<4}. {:<30} {:<30} {:<30}".format("","ID","NAME","STATUS"))
    for i,item in  enumerate(Knowledge_Objects):
        print("{:<4}. {:<30} {:<30} {:<30}".format(str(i),Knowledge_Objects[item].id,Knowledge_Objects[item].name[:30], Knowledge_Objects[item].status[:50]))
    
    print("-------------------")


# run install if the app is starated using poetry run uvicorn python_activator.api:app --reload
@app.on_event("startup")
async def startup_event():
    print(">>>>>> running startup event")
    object_directory = os.environ["COLLECTION_PATH"]
    manifest = process_manifest(object_directory)
    install_packages_from_directory(object_directory, manifest)
    del os.environ["COLLECTION_PATH"]
    del os.environ["MANIFEST_PATH"]


# run virtual server when running this .py file directly for debugging. It will look for objects at {code folder}/pyshelf
if __name__ == "__main__":
    print(">>>>>running with debug<<<<<")
    os.environ["MANIFEST_PATH"]="/home/faridsei/dev/test/package/manifest.json"
    #os.environ[
    #    "MANIFEST_PATH"
    #] = "https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/manifest.json"
    os.environ["COLLECTION_PATH"] = "/home/faridsei/dev/test/pyshelf/"

    uvicorn.run(app, host="127.0.0.1", port=8000)
