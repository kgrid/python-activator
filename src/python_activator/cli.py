from python_activator.api import *
import typer
import importlib

cli = typer.Typer()


# run the app using command line command run
@cli.command()
def run(collection_path: str = "", manifest_path: str = ""):
    object_directory = set_object_directory(collection_path)
    print("object directory is "+object_directory)
    if manifest_path:
        os.environ["MANIFEST_PATH"]=manifest_path
    if object_directory:
        os.environ["COLLECTION_PATH"]=object_directory
    
    uvicorn.run(app, host="127.0.0.1", port=8000)


def set_object_directory(collection_path: str) -> str:
    object_directory=""
    if (
        collection_path
    ):  # 1. run and pass --collection-path as input parameter:   "python-activator run --collection_path={your collection path}"
        object_directory = collection_path
        print(">>>>>running with input param<<<<<")
    elif os.environ.get(
        "COLLECTION_PATH"
    ):  # 2. set COLLECTION_PATH as an env variable and then:     "COLLECTION_PATH={your collection path} python-activator run"
        print(">>>>>running with environment variable<<<<<")
        object_directory = os.environ.get("COLLECTION_PATH")
        del os.environ["COLLECTION_PATH"]
    else:  # 3. run with python-activator run with no path provided. will consider {root of app}/pyshelf by default
        print(">>>>>running with default path (./pyshelf/)<<<<<")
    
    # 4. run debugger which will look for objects at hardcoded path in api.py
    # 5. run install packages from the given COLLECTION_PATH if the app is starated using "COLLECTION_PATH={your collection path} poetry run uvicorn python_activator.api:app --reload". The code to handle this is in api.py. If running in a virtual environment you could also use "COLLECTION_PATH={your collection path} uvicorn python_activator.api:app --reload"

    return object_directory

   
    
@cli.command()
def version():
    try:
        version = importlib.metadata.version("python-activator")
        print("Version:", version)
    except importlib.metadata.PackageNotFoundError:
        print("Package not found")
        

