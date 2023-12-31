import sys
import urllib.request
import zipfile
import pathlib
import os
from io import BytesIO
from pathlib import Path
from urllib import parse
import json
import logging

logger = logging.getLogger("Loader")
# Create a log handler that sends messages to stderr
stderr_handler = logging.StreamHandler(sys.stderr)

# Configure logging to use the stderr handler
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
    handlers=[stderr_handler],
)


class ManifestItem:
    def __init__(self, id: str, directory: str, status: str, error: str):
        self.id = id
        self.directory = directory
        self.status = status
        self.error = error

    def short_representation(self):
        return {"@id": self.id, "status": self.status, "error": self.error}


def load_package(object_directory, manifest_item):
    manifest_path = os.environ.get("ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH")
    scanned_directories = [f.name for f in os.scandir(object_directory) if f.is_dir()]
    ko_name = get_ko_name(manifest_path, manifest_item)

    # 1. if knowledge object already in the collection directory continue to the next ko in list
    if ko_name in scanned_directories:
        return

    # 2. extract the knowledge object from the zip file in the uri (local or remote) in object directory
    resource = open_resource(manifest_path, manifest_item)
    with resource:
        with zipfile.ZipFile(BytesIO(resource.read())) as zfile:
            zfile.extractall(object_directory)


def resolve_path(path, relative) -> str:
    uri = path
    if os.path.isabs(path):  # if a local path create the URI
        uri = pathlib.Path(path).as_uri()  # adds file:// if local path
    return parse.urljoin(uri, relative)


def open_resource(base, relative):
    resolved = resolve_path(base, relative)
    try:
        resource = urllib.request.urlopen(resolved)
    except:
        raise FileNotFoundError("Could not find resource file at " + resolved)

    return resource


def create_directory_if_not_exists(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            logging.error(f"Error creating directory '{path}': {e}")


def set_object_directory() -> str:
    if os.environ.get("ORG_KGRID_PYTHON_ACTIVATOR_COLLECTION_PATH"):
        object_directory = os.path.abspath(
            os.path.join(
                Path(os.environ["ORG_KGRID_PYTHON_ACTIVATOR_COLLECTION_PATH"]), ""
            )
        )
    else:
        object_directory = os.path.join(Path(os.getcwd()).joinpath("pyshelf"), "")
    create_directory_if_not_exists(object_directory)
    return object_directory


def get_ko_name(manifest_path, manifest_item) -> str:
    test = parse.urljoin(manifest_path, manifest_item)
    if os.path.isfile(parse.urljoin(manifest_path, manifest_item)):
        ko_name = os.path.splitext(os.path.basename(manifest_item))[0]
    else:
        ko_name = os.path.basename(manifest_item)
    return Path(ko_name).stem


def generate_manifest_from_directory(directory: str):
    manifest = []
    scanned_directories = [f.name for f in os.scandir(directory) if f.is_dir()]
    for sub_dir in scanned_directories:
        metadata = {}
        metadata["status"] = "uninitialized"
        try:
            with open(Path(directory).joinpath(sub_dir, "metadata.json"), "r") as file:
                metadata = json.load(file)
            metadata["status"] = "loaded"
            metadata["error"] = ""
        except Exception as e:
            metadata["error"] = repr(e)
            metadata["@id"] = sub_dir

        metadata["local_url"] = sub_dir
        manifest.append(metadata)

    with open(Path(directory).joinpath("local_manifest.json"), "w") as json_file:
        json.dump(manifest, json_file, indent=2)


def generate_manifest_from_loaded_list(directory: str, ko_list: list[ManifestItem]):
    manifest_path = os.environ.get("ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH")

    manifest = []
    scanned_directories = [f.name for f in os.scandir(directory) if f.is_dir()]
    for ko in ko_list:
        ko_name = get_ko_name(manifest_path, ko.directory)
        metadata = {}
        if ko_name in scanned_directories:
            try:
                with open(
                    Path(directory).joinpath(ko_name, "metadata.json"), "r"
                ) as file:
                    metadata = json.load(file)
            except:
                pass
        metadata["@id"] = ko.id
        metadata["local_url"] = ko_name
        metadata["status"] = ko.status
        metadata["error"] = ko.error
        manifest.append(metadata)

    with open(Path(directory).joinpath("local_manifest.json"), "w") as json_file:
        json.dump(manifest, json_file, indent=2)
