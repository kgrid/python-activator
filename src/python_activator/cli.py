from .api import *
import typer

cli = typer.Typer()


# run the app using command line command run
@cli.command()
def run(object_path: str = ""):
    if (
        object_path
    ):  # 1. run and pass --object-path as input parameter:   "python-activator run --object-path={your collection path}"
        object_directory = object_path
        print(">>>>>running with input param<<<<<")
    elif os.environ.get(
        "OBJECT_PATH"
    ):  # 2. set OBJECT_PATH as an env variable and then:     "OBJECT_PATH={your collection path} python-activator run"
        print(">>>>>running with environment variable<<<<<")
        object_directory = os.environ.get("OBJECT_PATH")
        del os.environ["OBJECT_PATH"]
    else:# 3. run with python-activator run with no path provided. will consider {root of app}/pyshelf as object location if any   
        print(">>>>>running with default path (./pyshelf/)<<<<<")
        object_directory = os.getcwd() + "/pyshelf"
        # 4. run debugger which will look for objects at hardcoded path in api.py
        # 5. run install packages from the given OBJECT_PATH if the app is starated using "OBJECT_PATH={your collection path} poetry run uvicorn python_activator.api:app --reload". The code to handle this is in api.py. If running in a virtual environment you could also use "OBJECT_PATH={your collection path} uvicorn python_activator.api:app --reload"
    install_packages_from_directory(object_directory)

    uvicorn.run(app, host="127.0.0.1", port=8000)


@cli.command()
def version():
    try:
        version = importlib.metadata.version("python-activator")
        print("Version:", version)
    except importlib.metadata.PackageNotFoundError:
        print("Package not found")
        

