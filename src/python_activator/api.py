import logging
import os
from typing import Any

from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import FastAPI, Request, Body
from fastapi.staticfiles import StaticFiles


from .Manifest import Manifest
from .loader import set_object_directory
from .exceptions import (
    EndpointNotFoundError,
    KONotFoundError,
    InvalidInputParameterError,
)
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.responses import FileResponse
import yaml


app = FastAPI()
app.mount("/demo", StaticFiles(directory=Path("demo")), name="demo")

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
    return JSONResponse(
        content={
            "title": exc.title,
            "detail": exc.detail,
        },
        status_code=exc.status_code,
    )


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
    return [{"@id": key, **obj} for key, obj in Routing_Dictionary.items()]


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
            "info": {"endpoint": endpoint, "inputs": body},
        }
    except Exception as e:
        raise InvalidInputParameterError(e)


@app.get("/kos/{ko_id:path}/service.yaml")
async def download_file(ko_id: str):
    full_path = str(
        Path(object_directory)
        .joinpath(Knowledge_Objects[ko_id].metadata["local_url"])
        .joinpath("service.yaml")
    )
    return FileResponse(full_path, filename="service.yaml")


@app.get("/kos/{ko_id:path}/service")
async def get_data(ko_id: str):
    # Load the YAML file
    full_path = str(
        Path(object_directory)
        .joinpath(Knowledge_Objects[ko_id].metadata["local_url"])
        .joinpath("service.yaml")
    )
    with open(full_path, "r") as yaml_file:
        data = yaml.safe_load(yaml_file)
    return {"data": data}


@app.get("/kos")
def endpoints(request: Request):
    for obj_key in Knowledge_Objects:
        if Knowledge_Objects[obj_key].metadata["status"] == "activated":
            Knowledge_Objects[obj_key].metadata["swaggerLink"] = (
                "https://editor.swagger.io?url="
                + request.url.__str__()
                + "/"
                + Knowledge_Objects[obj_key].metadata["@id"]
                + "/service.yaml"
            )
    return [obj.metadata for obj in Knowledge_Objects.values()]


@app.get("/kos/{ko_id:path}/doc", description="You should try out this route in your browser. It performs a redirection to the swagger editor for the ko which its id is provided.")
async def endpoint_detail(ko_id: str, request: Request):
    try:
        response = RedirectResponse(
            url="https://editor.swagger.io?url="
            + request.url.__str__().rstrip("/doc")
            + "/service.yaml"
        )
        return response
    except Exception as e:
        raise KONotFoundError(e)


@app.get("/kos/{ko_id:path}")
async def endpoint_detail(ko_id: str, request: Request):
    try:
        Knowledge_Objects[ko_id].metadata["swaggerLink"] = (
            "https://editor.swagger.io?url=" + request.url.__str__() + "/service.yaml"
        )
        return Knowledge_Objects[ko_id].metadata
    except Exception as e:
        raise KONotFoundError(e)


# run install if the app is starated using a web server like
# "poetry run uvicorn python_activator.api:app --reload"
@app.on_event("startup")
async def startup_event():
    logging.info(">>>>>> running startup event")
    manifest = Manifest()
    manifest.load_from_manifest()
    global Knowledge_Objects, Routing_Dictionary
    Knowledge_Objects, Routing_Dictionary = manifest.install_loaded_objects()

    global object_directory
    object_directory = set_object_directory()


##to be deleted, related to experience for openapi doc
#     for ko in Knowledge_Objects.values():
#         # Load your OpenAPI documentation
#         if ko.metadata["status"]=="activated":
#             full_path = str(Path(object_directory).joinpath(ko.metadata["local_url"]).joinpath("service.yaml"))
#             with open(full_path, 'r') as file:
#                 openapi_data = yaml.safe_load(file)

#             # Create FastAPI routes from the OpenAPI data
#             create_openapi_routes(openapi_data)
