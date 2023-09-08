import logging
import os
from typing import Any

from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import FastAPI, Request, Body


from python_activator.Manifest import Manifest
from python_activator.loader import set_object_directory
from python_activator.exceptions import (
    EndpointNotFoundError,
    KONotFoundError,
    InvalidInputParameterError,
)
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.responses import FileResponse
import yaml


app = FastAPI()
Knowledge_Objects = {}
Routing_Dictionary = {}
object_directory = ""

origins = [
    "http://editor.swagger.io",  # Add the domain of the Swagger Editor here
    "https://editor.swagger.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods, including OPTIONS
    allow_headers=["*"],
)

@app.exception_handler(EndpointNotFoundError)
@app.exception_handler(KONotFoundError)
@app.exception_handler(InvalidInputParameterError)
async def custom_exception_handler(request, exc):
    return JSONResponse(content={"title": exc.title,"detail": exc.detail,}, status_code=exc.status_code,)


async def custom_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith("/endpoints/") and request.method == "POST":
        logging.info(f"Request to endpoint {path}")

        response = await call_next(request)

        logging.info(f"Response to endpoint {path}: {response.status_code}")
    elif path.startswith("/kos/") and request.method == "POST":
        logging.info(f"Request to ko {path}")

        response = await call_next(request)

        logging.info(f"Response to ko {path}: {response.status_code}")    
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
    return [{"@id":key, **obj} for key, obj in Routing_Dictionary.items()]


@app.get("/endpoints/{endpoint_path:path}")
async def endpoint_detail(endpoint_path: str, request: Request):
    try:
        return Routing_Dictionary[endpoint_path]
    except Exception as e:
        raise EndpointNotFoundError(e)  # repr(e)


# endpoint to expose all packages
@app.post("/endpoints/{endpoint_path:path}")
async def execute_endpoint(
    endpoint_path: str,
    body: Any = Body(...),
):
    try:
        endpoint = Routing_Dictionary[endpoint_path]
    except Exception as e:
        raise EndpointNotFoundError(e)  # repr(e)

    try:
        function = endpoint["function"]
        result = function(body)
        return {
            "result": result,
            "info": {endpoint_path: endpoint, "inputs": body},
        }
    except Exception as e:
        raise InvalidInputParameterError(e)


@app.get("/kos/{ko_key:path}/service.yaml")
async def download_file(ko_key: str):
    full_path = str(Path(object_directory).joinpath(Knowledge_Objects[ko_key].metadata["local_url"]).joinpath("service.yaml"))
    return FileResponse(full_path, filename="service.yaml")



@app.get("/kos/{ko_key:path}/service")
async def get_data(ko_key: str):
    # Load the YAML file
    full_path = str(Path(object_directory).joinpath(Knowledge_Objects[ko_key].metadata["local_url"]).joinpath("service.yaml"))
    with open(full_path, "r") as yaml_file:
        data = yaml.safe_load(yaml_file)
    return {"data": data}


@app.get("/kos")
def endpoints(request: Request):
    for obj_key in Knowledge_Objects:
        if Knowledge_Objects[obj_key].metadata["status"] == "activated":
            Knowledge_Objects[obj_key].metadata["swaggerLink"] = (
                "https://editor.swagger.io?url="+request.url.__str__() + "/" + Knowledge_Objects[obj_key].metadata["@id"]+"/service.yaml"
            )
    return [obj.metadata for obj in Knowledge_Objects.values()]


@app.get("/kos/{ko_key:path}")
async def endpoint_detail(ko_key: str, request: Request):
    try:
        Knowledge_Objects[ko_key].metadata["swaggerLink"] = (
                "https://editor.swagger.io?url="+request.url.__str__() +"/service.yaml"
            )
        return Knowledge_Objects[ko_key].metadata
    except Exception as e:
        raise KONotFoundError(e)  


def finalize():
    global object_directory
    object_directory = set_object_directory()
    try:
        del os.environ["COLLECTION_PATH"]
        del os.environ["MANIFEST_PATH"]
    except Exception:
        pass

##to be deleted, related to experience for openapi doc
#from fastapi import Query
#from pydantic import BaseModel,Field, create_model
# class RequestBodyModel(BaseModel):
#     data: str
 
# # Function to generate FastAPI routes from the OpenAPI spec
# def create_openapi_routes(openapi_data):
#     location=openapi_data['servers'][0]['url']
#     for path, path_data in openapi_data['paths'].items():
#         for method, operation in path_data.items():
            
#             # Define a dictionary with field names and their types
#             field_definitions = {}
#             request_body = operation["requestBody"]
            
#             if "content" in request_body:
#                 json_content = request_body["content"].get("application/json", {}) 
#                 schema = json_content.get("schema", {})
                
#                 if "properties" in schema:
#                     for field_name, field_info in schema["properties"].items():
#                         field_type = Any
#                         field_example = field_info.get("example")
#                         field_definitions[field_name] = (field_type, field_example)
            
#             class RequestBodyModel(BaseModel):
#                 data: str = Field(
#                     ...,
#                     description="Your request data here.",
#                     example="Hello, World!"
#                 )
            
#             if request_body["content"].get("text/plain", {}):
#                 #RequestBodyModel.__config__.schema_extra =request_body["content"].get("text/plain", {}).get("schema", {}).get("properties", {}).get("example")
#                 RequestModel=RequestBodyModel
#             else:
#                 # Create a dynamic Pydantic BaseModel class
#                 RequestModel = create_model("DynamicModel"+location+path, **field_definitions)

#             # Create a function to handle the POST request with the defined request body format
#             async def post_endpoint(request_data: RequestModel):
#                 return request_data               
            
#             app.add_api_route(
#                 location+path,                
#                 endpoint=post_endpoint,             
#                 methods=[method.upper()],
#                 response_model=None,  # You can set a response model here if needed
#             )



# run install if the app is starated using a web server like
# "poetry run uvicorn python_activator.api:app --reload"
@app.on_event("startup")
async def startup_event():
    logging.info(">>>>>> running startup event")
    manifest = Manifest()
    manifest.load_from_manifest()
    global Knowledge_Objects, Routing_Dictionary
    Knowledge_Objects, Routing_Dictionary = manifest.install_loaded_objects()
    finalize()    
##to be deleted, related to experience for openapi doc
#     for ko in Knowledge_Objects.values():
#         # Load your OpenAPI documentation
#         if ko.metadata["status"]=="activated":
#             full_path = str(Path(object_directory).joinpath(ko.metadata["local_url"]).joinpath("service.yaml"))
#             with open(full_path, 'r') as file:
#                 openapi_data = yaml.safe_load(file)

#             # Create FastAPI routes from the OpenAPI data
#             create_openapi_routes(openapi_data)











    
