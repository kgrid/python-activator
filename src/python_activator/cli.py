import importlib.metadata
from typing import Optional
from python_activator.Manifest import Manifest
from python_activator.loader import generate_manifest_from_directory
import typer
from python_activator.api import *

cli = typer.Typer()


@cli.callback(invoke_without_command=True, no_args_is_help=True)
def no_command(
    version: Optional[bool] = typer.Option(None, "-v", "--version", is_eager=True)
):
    if version:
        try:
            v_str = importlib.metadata.version("python-activator")
        except AttributeError as e:
            print("N/A ({}) Are you running from source?".format(e.__doc__))
        except Exception as e:
            print("Version: N/A ({})".format(e.__doc__))
        else:
            print("Version: {}".format(v_str))
        finally:
            raise typer.Exit()


@cli.command()
def run(collection_path: str = "", manifest_path: str = ""):
    """Loads and installs knowledge objects and runs APIs."""
    object_directory = set_object_directory(collection_path)
    print("object directory is " + object_directory)
    if manifest_path:
        os.environ["MANIFEST_PATH"] = manifest_path
    if object_directory:
        os.environ["COLLECTION_PATH"] = object_directory

    uvicorn.run(app, host="127.0.0.1", port=8000)


@cli.command()
def create_manifest(collection_path: str = ""):
    """Creates local manifest for an existing collection."""
    generate_manifest_from_directory(collection_path)


@cli.command()
def load_from_manifest(collection_path: str = "", manifest_path: str = ""):
    """Loads KOs from a manifest and creates a local one."""
    object_directory = set_object_directory(collection_path)
    if manifest_path:
        os.environ["MANIFEST_PATH"] = manifest_path
    if object_directory:
        os.environ["COLLECTION_PATH"] = object_directory
    manifest = Manifest()
    manifest.load_from_manifest()


@cli.command()
def install_loaded_kos(collection_path: str = ""):
    """Installs KOs from a local manifest in a collection."""
    object_directory = set_object_directory(collection_path)
    if object_directory:
        os.environ["COLLECTION_PATH"] = object_directory
    manifest = Manifest()
    manifest.install_loaded_objects()


@cli.command()
def uninstall_kos(collection_path: str = ""):
    """Uninstalls KOs from a local manifest in a coolection."""
    try:
        object_directory = set_object_directory(collection_path)
        if object_directory:
            os.environ["COLLECTION_PATH"] = object_directory
        manifest = Manifest()
        manifest.uninstall_objects()
    except:
        pass


def set_object_directory(collection_path: str) -> str:
    object_directory = ""
    if (
        collection_path
    ):  
        object_directory = collection_path
        print(">>>>>running with input param<<<<<")
    elif os.environ.get(
        "COLLECTION_PATH"
    ): 
        print(">>>>>running with environment variable<<<<<")
        object_directory = os.environ.get("COLLECTION_PATH")
        del os.environ["COLLECTION_PATH"]
    else:  
        print(">>>>>running with default path (./pyshelf/)<<<<<")

    return object_directory


if __name__ == "__main__":
    cli()
