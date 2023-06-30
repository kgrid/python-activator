from typing import Union
from fastapi import FastAPI, Request, Header
import sys
import uvicorn
import importlib
import os
from os import path
import subprocess

app = FastAPI()


@app.get("/")
def hello():
    return {"Hello": "World10"}


@app.post("/{endpoint_key}")
async def execute_endpoint(
    endpoint_key: str, request: Request, content_type: str = Header(...)
):
    # get the method
    mymethod = getattr(ko_endpoint, "welcome")
    # run the imported method and pass the request json
    # if content_type == 'application/json':
    data = await request.json()
    # else:
    #   data="test"

    result = mymethod(data)

    return {"result": result}


def install_module():
    modulepath = (
        "/home/faridsei/dev/code/python-activator/src/python_activator/pyshelf/"
    )
    install_requirements(modulepath)

    # add module path to the sys path to be able to import external packages
    # TO DO: test how it works for windows installation
    if modulepath not in sys.path:
        sys.path.append(modulepath)

    # import package
    ko_endpoint = importlib.import_module("python_simple_1_0.src.welcome")
    return ko_endpoint


def install_requirements(modulepath):
    dependency_requirements = modulepath + "python_simple_1_0/requirements.txt"

    # uses 'pip install -r requirements.txt' to install requirements
    if path.exists(dependency_requirements):
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", dependency_requirements]
        )


ko_endpoint = install_module()

# only runs virtual server when running this .py file directly for debugging
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
