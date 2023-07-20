import os
from io import BytesIO
import pathlib
import zipfile
from urllib.parse import urlparse

import requests
import urllib

from python_activator.loader import load_packages


def test_process_local_manifest():
    os.environ["MANIFEST_PATH"] = "/home/faridsei/dev/test/manifest/manifest.json"
    load_packages("/home/faridsei/dev/test/pyshelf/")
    del os.environ["MANIFEST_PATH"]

    # Assert
    assert 1 == 1


def test_process_internet_manifest():
    os.environ[
        "MANIFEST_PATH"
    ] = "https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/manifest.json"
    load_packages("/home/faridsei/dev/test/pyshelf/")
    del os.environ["MANIFEST_PATH"]

    # Assert
    assert 1 == 1


def test_process_no_manifest():
    load_packages("/home/faridsei/dev/test/pyshelf/")

    # Assert
    assert 1 == 1


def test_using_url_to_extract_zip_remotely():
    destenation_path = "/home/faridsei/dev/test/pyshelf"
    response = requests.get(
        "https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/python-simple-v1.0.zip",
        stream=True,
    )
    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
        zip_ref.extractall(destenation_path)
    assert os.path.exists(destenation_path + "/python-simple-v1.0")


def test_using_local_path_to_extract_zip():
    destenation_path = "/home/faridsei/dev/test/pyshelf"
    # response = requests.get('file:///home/faridsei/dev/test/package/python-multimime-v1.0.zip', stream=True)
    with zipfile.ZipFile(
        "/home/faridsei/dev/test/package/python-multimime-v1.0.zip"
    ) as zip_ref:
        zip_ref.extractall(destenation_path)
    assert os.path.exists(destenation_path + "/python-simple-v1.0")


def test_using_uri_to_extract_zip():
    destenation_path = "/home/faridsei/dev/test/pyshelf"

    uri = get_uri(
        "https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/python-multimime-v1.0.zip"
    )
    # uri=get_uri('file:///home/faridsei/dev/test/package/python-multimime-v1.0.zip')

    with urllib.request.urlopen(uri) as response:
        with zipfile.ZipFile(BytesIO(response.read())) as zfile:
            zfile.extractall(destenation_path)
    assert os.path.exists(destenation_path + "/python-multimime-v1.0")


# def test_formatting_dictionary_of_object_to_json():
#    assert 1!=1


def get_uri(path: str):
    uri = path
    if os.path.exists(path):  # if a local path create the URI
        uri = pathlib.Path(path).as_uri()  # adds file:// if local path
    return uri


def get_base_uri(uri):
    parsed_uri = urlparse(uri)
    base_uri = f"{parsed_uri.scheme}://{parsed_uri.netloc}"
    return base_uri
