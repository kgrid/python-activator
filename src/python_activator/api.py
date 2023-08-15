import os
from typing import Any
from fastapi.responses import RedirectResponse
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request,Response, Body
from python_activator.Manifest import Manifest
from pathlib import Path
import logging

app = FastAPI()
Knowledge_Objects = {}
Routing_Dictionary={}
object_directory=""

async def custom_middleware(request: Request, call_next):
    endpoint_path = request.url.path
    if endpoint_path.startswith("/endpoints/") and request.method == "POST":
        logging.info(f"Request to endpoint {endpoint_path}")
        
        response = await call_next(request)
        
        logging.info(f"Response to endpoint {endpoint_path}: {response.status_code}")
    else:
        response = await call_next(request)
        
    return response
app.middleware("http")(custom_middleware)

@app.get(
    "/",
    include_in_schema=False,
)
async def root(request: Request):
    response = RedirectResponse(url="/docs")
    return response
    

@app.get("/endpoints")
def endpoints(request: Request):
    for obj_key in Knowledge_Objects:
        if Knowledge_Objects[obj_key].status == "installed":
            Knowledge_Objects[obj_key].url = (
                request.url.__str__() + "/" + Knowledge_Objects[obj_key].metadata["@id"]
            )

    return Knowledge_Objects


@app.get("/endpoints/{endpoint_key:path}")
async def endpoint_detail(endpoint_key: str):
    return Knowledge_Objects[endpoint_key]


# endpoint to expose all packages
@app.post("/endpoints/{endpoint_path:path}")
async def execute_endpoint(
    endpoint_path: str,
    body: Any = Body(...),
):
    service_path=""
    try:
        endpoint_key,endpoint_route=route_endpoint(endpoint_path)            
        service_path=str(Path(object_directory).joinpath(Knowledge_Objects[endpoint_key].local_url).joinpath("service.yaml"))    
        result = await Knowledge_Objects[endpoint_key].execute(body,endpoint_route)
        return {"result": result, "info": {"ko": Knowledge_Objects[endpoint_key].metadata, "inputs": body }}
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=({"error": repr(e), "endpoint_path": endpoint_path, "more info":service_path})
        )    
    


def finalize():
    global object_directory
    object_directory=os.environ["COLLECTION_PATH"]
    try:
        del os.environ["COLLECTION_PATH"]
        del os.environ["MANIFEST_PATH"]
    except Exception as e:
        print("error deleting env variables")

    print("-------------------\nPackages installed:")
    print("{:<4}. {:<30} {:<30} {:<30}".format("", "ID", "NAME", "STATUS"))
    for i, item in enumerate(Knowledge_Objects):
        print(
            "{:<4}. {:<30} {:<30} {:<30}".format(
                str(i),
                item,
                Knowledge_Objects[item].local_url[:30],
                Knowledge_Objects[item].status[:50],
            )
        )
    print("-------------------")

def route_endpoint(endpoint_path):
        endpoint_key=endpoint_path
        endpoint_route=""
        if endpoint_path in Routing_Dictionary.keys():
            endpoint_key=Routing_Dictionary[endpoint_path].id
            endpoint_route=Routing_Dictionary[endpoint_path].route
        return endpoint_key,endpoint_route
    
        
# run install if the app is starated using a web server like "poetry run uvicorn python_activator.api:app --reload"
@app.on_event("startup")
async def startup_event():
    print(">>>>>> running startup event")
    manifest = Manifest()
    manifest.load_from_manifest()
    global Knowledge_Objects, Routing_Dictionary
    Knowledge_Objects,Routing_Dictionary = manifest.install_loaded_objects()
    finalize()

# run virtual server when running this .py file directly for debugging. It will look for objects at {code folder}/pyshelf
if __name__ == "__main__":
    print(">>>>>running with debug<<<<<")
    os.environ["MANIFEST_PATH"] = "/home/faridsei/dev/code/python-activator/tests/fixtures/installfiles/manifest.json"
    # os.environ["MANIFEST_PATH"] = "https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/manifest.json"
    os.environ["COLLECTION_PATH"] = "/home/faridsei/dev/test/pyshelf"
    uvicorn.run(app, host="127.0.0.1", port=8000)
