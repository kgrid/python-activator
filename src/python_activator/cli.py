import importlib.metadata
from typing import Optional
from python_activator.Manifest import Manifest
from python_activator.loader import generate_manifest_from_directory
import typer
from python_activator.api import *
import uvicorn 

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
    set_collection_path(collection_path)
    if manifest_path:
        os.environ["ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH"] = manifest_path


    uvicorn.run(app, host="127.0.0.1", port=8000)


@cli.command()
def create_manifest(collection_path: str = ""):
    """Creates local manifest for an existing collection."""
    generate_manifest_from_directory(collection_path)


@cli.command()
def load_from_manifest(collection_path: str = "", manifest_path: str = ""):
    """Loads KOs from a manifest and creates a local one."""
    set_collection_path(collection_path)
    if manifest_path:
        os.environ["ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH"] = manifest_path

    manifest = Manifest()
    manifest.load_from_manifest()


@cli.command()
def install_loaded_kos(collection_path: str = ""):
    """Installs KOs from a local manifest in a collection."""
    set_collection_path(collection_path)

    manifest = Manifest()
    manifest.install_loaded_objects()


@cli.command()
def uninstall_kos(collection_path: str = ""):
    """Uninstalls KOs from a local manifest in a coolection."""
    try:
        set_collection_path(collection_path)

        manifest = Manifest()
        manifest.uninstall_objects()
    except:
        pass


def set_collection_path(collection_path: str) -> str:    
    if (collection_path):  
        os.environ["ORG_KGRID_PYTHON_ACTIVATOR_COLLECTION_PATH"] = collection_path
        
    


if __name__ == "__main__":
    cli()
