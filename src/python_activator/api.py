import logging
import os
from typing import Any
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import FastAPI, HTTPException, Request, Body
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

app = FastAPI(
    title="Python Activator",
    description="This activator is a reference implementation of kgrid activator specs. It activates knowledge objects that are implemented using Python and comply to kgrid specs.",
    version="0.7.0",
    contact={
        "name": "kgrid developers",
        "url": "https://kgrid.org/",
        "email": "kgrid-developers@umich.edu",
    },
)

# Demo app using static file
app.mount("/demo", StaticFiles(directory=Path("demo")), name="demo")

Knowledge_Objects = {}
Routing_Dictionary = {}
object_directory = ""

# Add middleware to control access to APIs
origins = [
    "http://editor.swagger.io",  # Add the domain of the external systems using apis. for all origins use ["*"]
    "https://editor.swagger.io",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods, including OPTIONS
    allow_headers=["*"],
)


# Prepare custom exceptions and their response
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


# Add logging for main api calls
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


# Add middleware for logging api calls
app.middleware("http")(custom_middleware)


@app.get(
    "/",
    include_in_schema=False,
)
async def root(request: Request):
    response = RedirectResponse(url="/docs")
    return response


@app.get(
    "/endpoints",
    summary="",
    description="Gives the list of activated endpoints and their detail.",
)
def endpoints(request: Request):
    return [{"@id": key, **obj} for key, obj in Routing_Dictionary.items()]


@app.get(
    "/endpoints/{endpoint_path:path}",
    summary="Endpoint Detail",
    description="Gives detail for a specific endpoint.",
)
async def endpoint_detail(endpoint_path: str, request: Request):
    try:
        return Routing_Dictionary[endpoint_path]
    except Exception as e:
        raise EndpointNotFoundError(e)  # repr(e)


@app.post(
    "/endpoints/{endpoint_path:path}",
    summary="Execute Endpoint",
    description="Execute the KO function behind a specific endpoint.",
)
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


@app.get(
    "/kos/{ko_id:path}/service",
    summary="Download Service File",
    description="Provide access to the service.yaml for each ko at /kos/{{ko_id}}/service.",
)
async def download_file(ko_id: str):
    try:
        file = Knowledge_Objects[ko_id].metadata.get(
            "hasServiceSpecification", "service.yaml"
        )  # default to service.yaml
        # if version 2 (or after) use service file defined in python service
        if (
            Knowledge_Objects[ko_id].metadata.get("koio:kgrid", "") != ""
            and Knowledge_Objects[ko_id].metadata["koio:kgrid"] == "2"
        ):
            services = Knowledge_Objects[ko_id].metadata["koio:hasService"]
            for service in services:
                if (
                    service["@type"] == "API"
                        and service.get("implementedBy", "") != "") :
                    implementations=service["implementedBy"] 
                    for implementation in implementations:
                        if(implementation.get("@type", "")== "koio:org.kgrid.python-activator"):
                            file = service.get("hasServiceSpecification", "service.yaml")
                            break
    except Exception as e:
        raise KONotFoundError(e)

    full_path = str(
        Path(object_directory)
        .joinpath(Knowledge_Objects[ko_id].metadata["local_url"])
        .joinpath(file)
    )
    headers = {
        "Content-Type": "application/x-yaml",  # or "text/yaml"
        "Content-Disposition": f"attachment; filename={file}",
    }
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(full_path, headers=headers)


@app.get(
    "/kos",
    summary="KOs List and Detail",
    description="Gives the list of KOs and their detail.",
)
def endpoints(request: Request):
    for obj_key in Knowledge_Objects:
        if Knowledge_Objects[obj_key].metadata["status"] == "activated":
            Knowledge_Objects[obj_key].metadata["documentation"] = (
                request.url.__str__()
                + "/"
                + Knowledge_Objects[obj_key].metadata["@id"]
                + "/doc"
            )
    return [obj.metadata for obj in Knowledge_Objects.values()]


@app.get(
    "/kos/{ko_id:path}/doc",
    summary="KO Documentation",
    description="This API redirects to the swagger editor for ko with id {ko_id}. This route should be used only in the browser.",
)
async def endpoint_detail(ko_id: str, request: Request):
    try:
        response = RedirectResponse(
            url="https://editor.swagger.io?url="
            + request.url.__str__().rstrip("/doc")
            + "/service"
        )
        return response
    except Exception as e:
        raise KONotFoundError(e)


@app.get(
    "/kos/{ko_id:path}",
    summary="KO Detail",
    description="Gives a specific KO and its detail.",
)
async def endpoint_detail(ko_id: str, request: Request):
    try:
        Knowledge_Objects[ko_id].metadata["documentation"] = (
            request.url.__str__() + "/doc"
        )
        return Knowledge_Objects[ko_id].metadata
    except Exception as e:
        raise KONotFoundError(e)


# Load and install KOs
# startup runs if the app is starated using a web server like
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
