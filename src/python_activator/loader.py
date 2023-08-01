import urllib.request
import zipfile
import pathlib
import os
from io import BytesIO
from pathlib import Path
from urllib import parse


def load_package(object_directory, manifest_item):
    manifest_path = os.environ.get("MANIFEST_PATH")
    scanned_directories = [f.name for f in os.scandir(object_directory) if f.is_dir()]

    if os.path.isfile(manifest_item):
        ko_name = os.path.splitext(os.path.basename(manifest_item))[0]
    else:
        ko_name = os.path.basename(manifest_item)

    # 1. if knowledge object already in the collection directory continue to the next ko in list
    if ko_name in scanned_directories:
        return

    # 2. extract the knowledge object from the zip file in the uri (local or remote) in object directory
    resource = open_resource(manifest_path, manifest_item)
    with resource:
        with zipfile.ZipFile(BytesIO(resource.read())) as zfile:
            zfile.extractall(object_directory)


def resolve_path(path, relative):
    uri = path
    if os.path.isabs(path):  # if a local path create the URI
        uri = pathlib.Path(path).as_uri()  # adds file:// if local path
    return parse.urljoin(uri, relative)


def open_resource(base, relative):
    resolved = resolve_path(base, relative)
    try:
        resource = urllib.request.urlopen(resolved)
    except:
        raise FileNotFoundError("Could not find resource file.")

    return resource


def create_directory_if_not_exists(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            print(f"Error creating directory '{path}': {e}")


def set_object_directory():
    if os.environ.get("COLLECTION_PATH"):
        object_directory = os.path.join(Path(os.environ["COLLECTION_PATH"]), "")
    else:
        object_directory = os.path.join(Path(os.getcwd()).joinpath("pyshelf"), "")
    create_directory_if_not_exists(object_directory)
    return object_directory
