import os
import importlib
import json
import subprocess
import sys
from pathlib import Path

import uvicorn
import yaml
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.openapi.docs import get_swagger_ui_html

from python_activator.loader import load_packages


class knowledge_object:
    def __init__(self, name, status, function, id, url, entry):
        self.id = id
        self.name = name
        self.status = status
        self.function = function
        self.url = url
        self.entry = entry

    async def execute(self, request):
        data = (
            await request.json()
        )  # if content_type == 'application/json': data = await request.json() else:   data="test"
        try:
            return self.function(data)
        except TypeError as e:
            raise HTTPException(
                status_code=422, 
                detail={"status": self.status, "cause": e.__cause__}
                )


app = FastAPI()
Knowledge_Objects = {}
object_directory = ""  # used for location of knowledge objects


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="API Documentation",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    return app.openapi()


@app.get(
    "/",
    include_in_schema=False,
)
async def root(request: Request):
    return {
        "endpoints": request.url.__str__() + "endpoints",
        "execute": request.url.__str__() + "endpoints/{id}",
    }


@app.get("/endpoints")
def endpoints(request: Request):
    for obj_key in Knowledge_Objects:
        Knowledge_Objects[obj_key].url = (
            request.url.__str__() + "/" + Knowledge_Objects[obj_key].id
        )
    return Knowledge_Objects


@app.get("/endpoints/{endpoint_key:path}")
async def endpoint_detail(endpoint_key: str):
    return Knowledge_Objects[endpoint_key]


# endpoint to expose all packages
@app.post("/endpoints/{endpoint_key:path}")
async def execute_endpoint(
    endpoint_key: str, request: Request, content_type: str = Header(...)
):
    try:
        result = await Knowledge_Objects[endpoint_key].execute(request)
        return result
    except KeyError as e:
        raise HTTPException(
            status_code=404, detail=({"test": e.args, "test1": e.__str__})
        )


# Install requirements using the requirements.txt file for each package
def install_requirements(modulepath):
    dependency_requirements = Path(modulepath).joinpath("requirements.txt")

    # To Do: using pip install bellow explore installing requirements in a folder specific to the ko
    #       you may need to add that folder to the sys.path

    # uses 'pip install -r requirements.txt' to install requirements
    if os.path.exists(dependency_requirements):
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", dependency_requirements]
        )


# look into the main directory that has all the packages and have the python ones installed
def install_packages(directory, manifest: dict):
    for ko in manifest:
        install_module(directory, manifest[ko])
    list_installed_packages()


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
                ko.name,
                "Knowledge object is not activated. It is not a python object.",
                None,
                metadata["@id"],
                "",
                "",
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
            ko.name,
            "Activated",
            mymethod,
            metadata["@id"],
            "",
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


# run install if the app is starated using poetry run uvicorn python_activator.api:app --reload
@app.on_event("startup")
async def startup_event():
    print(">>>>>> running startup event")
    if os.environ.get("COLLECTION_PATH"):
        object_directory = os.path.join(Path(os.environ["COLLECTION_PATH"]), "")
    else:
        object_directory = os.path.join(Path(os.getcwd()).joinpath("pyshelf"), "")

    manifest = load_packages(object_directory)
    install_packages(object_directory, manifest)
    try:
        del os.environ["COLLECTION_PATH"]
        del os.environ["MANIFEST_PATH"]
    except Exception as e:
        print("error deleting env variables")


# run virtual server when running this .py file directly for debugging. It will look for objects at {code folder}/pyshelf
if __name__ == "__main__":
    print(">>>>>running with debug<<<<<")
    # os.environ["MANIFEST_PATH"]="/home/faridsei/dev/test/package/manifest.json"
    # os.environ["MANIFEST_PATH"] = "https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/manifest.json"
    os.environ["COLLECTION_PATH"] = "/home/faridsei/dev/test/pyshelf/"
    uvicorn.run(app, host="127.0.0.1", port=8000)
