import os
from io import BytesIO
import pathlib
import zipfile
from urllib.parse import urlparse
import requests
import urllib
from pathlib import Path
from python_activator.loader import load_packages,get_uri


def test_process_local_manifest():
    os.environ["MANIFEST_PATH"] = "/home/faridsei/dev/test/manifest/manifest.json"
    os.environ["COLLECTION_PATH"] = "/home/faridsei/dev/test/pyshelf/"
    load_packages()
    del os.environ["MANIFEST_PATH"]

    # Assert
    assert 1 == 1


def test_process_internet_manifest():
    os.environ[
        "MANIFEST_PATH"
    ] = "https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/manifest.json"
    os.environ["COLLECTION_PATH"] = "/home/faridsei/dev/test/pyshelf/"
    load_packages()
    del os.environ["MANIFEST_PATH"]

    # Assert
    assert 1 == 1


def test_process_no_manifest():
    os.environ["COLLECTION_PATH"] = "/home/faridsei/dev/test/pyshelf/"
    load_packages()

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

def test_get_uri():
    uri=get_uri("/home/faridsei/dev/test/manifest/python-multimime-v1.0.zip")
    assert uri #if any
    uri=get_uri("https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/python-multimime-v1.0.zip")
    assert uri #if any

def is_valid_uri(uri):
    try:
        result = urlparse(uri)
        if result.scheme and result.netloc:
            return True  # Valid URL
        elif not result.scheme and not result.netloc:
            # Check if it's a valid local file path
            file_path = Path(result.path)
            return file_path.is_absolute() and file_path.exists()
        else:
            return False  # Invalid URI
    except:
        return False  # Invalid URI
# def test_formatting_dictionary_of_object_to_json():
#    assert 1!=1




